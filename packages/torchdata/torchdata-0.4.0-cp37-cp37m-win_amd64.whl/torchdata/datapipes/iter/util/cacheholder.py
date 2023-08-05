# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import functools
import hashlib
import inspect
import os.path
import sys
import time
import warnings

from collections import deque
from functools import partial
from typing import Any, Callable, Deque, Dict, Iterator, List, Optional, TypeVar

try:
    import portalocker
except ImportError as e:
    if os.name == "nt" and str(e).startswith("DLL load failed while importing"):
        print(
            "Please take a look at FAQ in https://github.com/pytorch/data#frequently-asked-questions-faq"
            "for the solution of this Error."
        )
    raise


from torch.utils.data.datapipes.utils.common import _check_lambda_fn, DILL_AVAILABLE

from torch.utils.data.graph import traverse
from torchdata.datapipes import functional_datapipe
from torchdata.datapipes.iter import FileLister, IterDataPipe

if DILL_AVAILABLE:
    import dill

    dill.extend(use_dill=False)

T_co = TypeVar("T_co", covariant=True)

PROMISE_FILE_DELETE_TIMEOUT = 30
PROMISE_FILE_DELETE_RETRY_INTERVAL = 0.005


@functional_datapipe("in_memory_cache")
class InMemoryCacheHolderIterDataPipe(IterDataPipe[T_co]):
    r"""
    Stores elements from the source DataPipe in memory, up to a size limit
    if specified (functional name: ``in_memory_cache``). This cache is FIFO - once the cache is full,
    further elements will not be added to the cache until the previous ones are yielded and popped off from the cache.

    Args:
        source_dp: source DataPipe from which elements are read and stored in memory
        size: The maximum size (in megabytes) that this DataPipe can hold in memory. This defaults to unlimited.

    Example:
        >>> from torchdata.datapipes.iter import IterableWrapper
        >>> source_dp = IterableWrapper(range(10))
        >>> cache_dp = source_dp.in_memory_cache(size=5)
        >>> list(cache_dp)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    size: Optional[int] = None
    idx: int

    def __init__(self, source_dp: IterDataPipe[T_co], size: Optional[int] = None) -> None:
        self.source_dp: IterDataPipe[T_co] = source_dp
        # cache size in MB
        if size is not None:
            self.size = size * 1024 * 1024
        self.cache: Optional[Deque] = None
        self.idx: int = 0

    def __iter__(self) -> Iterator[T_co]:
        if self.cache:
            for idx, data in enumerate(self.source_dp):
                if idx < self.idx:
                    yield data
                else:
                    break
            yield from self.cache
        else:
            # Local cache
            cache: Deque = deque()
            idx = 0
            for data in self.source_dp:
                cache.append(data)
                # Cache reaches limit
                if self.size is not None and sys.getsizeof(cache) > self.size:
                    cache.popleft()
                    idx += 1
                yield data
            self.cache = cache
            self.idx = idx

    def __len__(self) -> int:
        try:
            return len(self.source_dp)
        except TypeError:
            if self.cache:
                return self.idx + len(self.cache)
            else:
                raise TypeError(f"{type(self).__name__} instance doesn't have valid length until the cache is loaded.")


def _generator_to_list(gen_fn):
    def list_fn(*args, **kwargs):
        gen = gen_fn(*args, **kwargs)
        return list(gen)

    return list_fn


def _hash_check(filepath, hash_dict, hash_type):

    if filepath not in hash_dict:
        return False

    if hash_type == "sha256":
        hash_func = hashlib.sha256()
    else:
        hash_func = hashlib.md5()

    # with portalocker.Lock(filepath, "rb", flags=portalocker.LockFlags.SHARED) as f:
    # TODO(VitalyFedyunin): Line above will require all readers (Win) to obtain proper locks,
    # I'm putting it on hold as we need to modify PyTorch core codebase heavily.
    with open(filepath, "rb") as f:
        chunk = f.read(1024 ** 2)
        while chunk:
            hash_func.update(chunk)
            chunk = f.read(1024 ** 2)

    return hash_func.hexdigest() == hash_dict[filepath]


def _promise_filename(filename):
    return filename + ".promise"


@functional_datapipe("on_disk_cache")
class OnDiskCacheHolderIterDataPipe(IterDataPipe):
    """
    Caches the outputs of multiple DataPipe operations to local files, which are
    typically performance bottleneck such download, decompress, and etc (functional name: ``on_disk_cache``).

    Must use ``.end_caching()`` to stop tracing the sequence of DataPipe operations and save the results to local files.

    Args:
        source_datapipe: IterDataPipe
        filepath_fn: Given data from ``source_datapipe``, returns file path(s) on local file system.
            Single file path, tuple or list of file paths is accepted as return type.
            And, generator function that yields file paths is also allowed.
            As default, data from ``source_datapipe`` is directly used to determine the existency of cache.
        hash_dict: A Dictionary mapping file names to their corresponding hashes. If ``hash_dict`` is specified,
            the extra hash check will be attached before saving data to local file system. If the data
            doesn't meet the hash, the pipeline will raise an Error.
        hash_type: The type of hash function to apply
        extra_check_fn: Optional function to carry out extra validation on
            the given file path from ``filepath_fn``.

    Example:
        >>> from torchdata.datapipes.iter import IterableWrapper, HttpReader
        >>> url = IterableWrapper(["https://path/to/filename", ])
        >>> def _filepath_fn(url):
        >>>     temp_dir = tempfile.gettempdir()
        >>>     return os.path.join(temp_dir, os.path.basename(url))
        >>> hash_dict = {"expected_filepath": expected_MD5_hash}
        >>> cache_dp = url.on_disk_cache(filepath_fn=_filepath_fn, hash_dict=_hash_dict, hash_type="md5")
        >>> # You must call ``.end_caching`` at a later point to stop tracing and save the results to local files.
        >>> cache_dp = HttpReader(cache_dp).end_caching(mode="wb", filepath_fn=_filepath_fn)
    """

    _temp_dict: Dict = {}

    def __init__(
        self,
        source_datapipe: IterDataPipe,
        filepath_fn: Optional[Callable] = None,
        hash_dict: Dict[str, str] = None,
        hash_type: str = "sha256",
        extra_check_fn: Optional[Callable[[str], bool]] = None,
    ):
        self.source_datapipe = source_datapipe

        _check_lambda_fn(filepath_fn)
        filepath_fn = _generator_to_list(filepath_fn) if inspect.isgeneratorfunction(filepath_fn) else filepath_fn

        if hash_dict is not None and hash_type not in ("sha256", "md5"):
            raise ValueError("Invalid hash_type requested, should be one of {}".format(("sha256", "md5")))
        OnDiskCacheHolderIterDataPipe._temp_dict[self] = (filepath_fn, hash_dict, hash_type, extra_check_fn)

        self._end_caching_flag: bool = False

    def __iter__(self):
        if self._end_caching_flag:
            yield from self.source_datapipe
        else:
            # In case of BC breaking, use RuntimeError for now. Warning is another option
            raise RuntimeError("Please call `end_caching()` before iteration.")

    def __add__(self, other_datapipe):
        raise RuntimeError("`OnDiskCacheHolder` doesn't support add operation")

    # Since Demux is using this function, we should not attach it to OnDiskCacheHolder instance.
    # Otherwise, it would cause infinite recursion in graph traversal
    @staticmethod
    def _cache_check_fn(data, filepath_fn, hash_dict, hash_type, extra_check_fn):
        filepaths = data if filepath_fn is None else filepath_fn(data)
        result = True
        if not isinstance(filepaths, (list, tuple)):
            filepaths = [
                filepaths,
            ]

        for filepath in filepaths:
            cached_file_exists = True
            if not os.path.exists(filepath):
                cached_file_exists = False
            elif hash_dict is not None and not _hash_check(filepath, hash_dict, hash_type):
                cached_file_exists = False
            elif extra_check_fn is not None and not extra_check_fn(filepath):
                cached_file_exists = False

            if not cached_file_exists:
                promise_filepath = _promise_filename(filepath)
                dirname = os.path.dirname(promise_filepath)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                with portalocker.Lock(promise_filepath, "a+", flags=portalocker.LockFlags.EXCLUSIVE) as promise_fh:
                    promise_fh.seek(0)
                    data = promise_fh.read()
                    # TODO(VitalyFedyunin): Potentially there is old .promise file from previous failed run, we
                    # need to somehow propagate uniq session id for dataloader, save and compare it here,
                    # raising error
                    file_exists = len(data) > 0
                    if not file_exists:
                        result = False
                        promise_fh.seek(0)
                        promise_fh.write("[dataloader session uid]")
                        promise_fh.truncate()
                        promise_fh.flush()

        return result

    def _end_caching(self):
        filepath_fn, hash_dict, hash_type, extra_check_fn = OnDiskCacheHolderIterDataPipe._temp_dict.pop(self)

        todo_dp, cached_dp = self.source_datapipe.demux(
            2,
            partial(
                OnDiskCacheHolderIterDataPipe._cache_check_fn,
                filepath_fn=filepath_fn,
                hash_dict=hash_dict,
                hash_type=hash_type,
                extra_check_fn=extra_check_fn,
            ),
        )
        # Cached: keep filepath(s)
        cached_dp = cached_dp.map(fn=filepath_fn)
        # Convert list back to single elements
        cached_dp = cached_dp.unbatch(-1)

        self.source_datapipe = todo_dp
        self._end_caching_flag = True
        return cached_dp


def _read_bytes(fd):
    return b"".join(fd)


def _read_str(fd):
    return "".join(fd)


def _find_promise_file(filename):
    promise_filename = _promise_filename(filename)
    while not os.path.exists(promise_filename):
        dirname = os.path.dirname(promise_filename)
        if dirname == os.path.dirname(dirname):
            promise_filename = _promise_filename(filename)
            break
        promise_filename = _promise_filename(dirname)
    return promise_filename


def _is_promise_pending(promise_filename):
    return os.path.exists(promise_filename)


def _wait_promise_fn(timeout, filename):
    promise_filename = _find_promise_file(filename)
    start = time.time()
    while _is_promise_pending(promise_filename):
        time.sleep(0.01)
        if time.time() - start > timeout:
            raise Exception(
                f"OnDiskCache Exception: {filename} expected to be written by different process, "
                + f"but file is not ready in {timeout} seconds."
            )
    return filename


class _FulfilledPromisesIterDataPipe(IterDataPipe):
    def __init__(self, source_datapipe):
        self.source_datapipe = source_datapipe

    @staticmethod
    def _del_promise_file(promise_filename, filename):
        if os.path.exists(promise_filename):
            retry = True
            start = time.time()
            while retry:
                retry = False
                try:
                    os.unlink(promise_filename)
                except Exception as e:
                    # Workaround about Windows not letting to delete file, while it is open by another process
                    retry = True
                    if time.time() - start > PROMISE_FILE_DELETE_TIMEOUT:
                        raise Exception("Timeout while trying to recover from the ", type(e), e)
                    time.sleep(PROMISE_FILE_DELETE_RETRY_INTERVAL)
        else:
            warnings.warn(
                f"Attempt to mark {promise_filename} promise (base of file {filename}) as fulfilled failed. Potentially missmatching filename functions of on_disk_cache and end_cache."
            )

    def __iter__(self):
        old_promise_filename = None
        old_filename = None
        first_entry = True
        # TODO(VitalyFedyunin): Limit buffer size here. It is only contains file names from archive,
        # but better be save than sorry.
        buffer: List[Any] = []
        for filename in self.source_datapipe:
            promise_filename = _find_promise_file(filename)
            if not first_entry:
                buffer.append(old_filename)
                if old_promise_filename != promise_filename:
                    self._del_promise_file(old_promise_filename, old_filename)
                    yield from buffer
                    buffer = []
            old_promise_filename = promise_filename
            old_filename = filename
            first_entry = False
        if not first_entry:
            buffer.append(old_filename)
            self._del_promise_file(old_promise_filename, old_filename)
            yield from buffer


@functional_datapipe("end_caching")
class EndOnDiskCacheHolderIterDataPipe(IterDataPipe):
    """
    Indicates when the result of prior DataPipe will be saved local files specified
    by ``filepath_fn`` (functional name: ``end_caching``). Moreover, the result of source DataPipe
    is required to be a tuple of metadata and data, or a tuple of metadata and file handle.

    Args:
        datapipe: IterDataPipe with at least one ``OnDiskCacheHolder`` in the graph.
        mode: Mode in which the cached files are opened to write the data on disk. This is needed
            to be aligned with the type of data or file handle from ``datapipe``. ``"wb"`` is used by default.
        filepath_fn: Optional function to extract filepath from the metadata from ``datapipe``.
            By default, it would directly use the metadata as file path.
        same_filepath_fn: Set to ``True`` to use same ``filepath_fn`` from the ``OnDiskCacheHolder``.
        skip_read: Boolean value to skip reading the file handle from ``datapipe``.
            By default, reading is enabled and reading function is created based on the ``mode``.
        timeout: Integer value of seconds to wait for uncached item to be written to disk

    Example:
        >>> from torchdata.datapipes.iter import IterableWrapper, HttpReader
        >>> url = IterableWrapper(["https://path/to/filename", ])
        >>> def _filepath_fn(url):
        >>>     temp_dir = tempfile.gettempdir()
        >>>     return os.path.join(temp_dir, os.path.basename(url))
        >>> hash_dict = {"expected_filepath": expected_MD5_hash}
        >>> # You must call ``.on_disk_cache`` at some point before ``.end_caching``
        >>> cache_dp = url.on_disk_cache(filepath_fn=_filepath_fn, hash_dict=_hash_dict, hash_type="md5")
        >>> # You must call ``.end_caching`` at a later point to stop tracing and save the results to local files.
        >>> cache_dp = HttpReader(cache_dp).end_caching(mode="wb", filepath_fn=_filepath_fn)
    """

    def __new__(cls, datapipe, mode="wb", filepath_fn=None, *, same_filepath_fn=False, skip_read=False, timeout=300):
        if filepath_fn is not None and same_filepath_fn:
            raise ValueError("`filepath_fn` is mutually exclusive with `same_filepath_fn`")

        graph = traverse(datapipe, only_datapipe=True)
        # Get the last CacheHolder
        cache_holder = EndOnDiskCacheHolderIterDataPipe._recursive_search(graph)
        if cache_holder is None:
            raise RuntimeError("Expected `OnDiskCacheHolder` existing in pipeline when `end_caching` is invoked")
        if cache_holder._end_caching_flag:
            raise RuntimeError("`end_caching` can only be invoked once per `OnDiskCacheHolder`")

        _filepath_fn, _hash_dict, _hash_type, _ = OnDiskCacheHolderIterDataPipe._temp_dict[cache_holder]
        cached_dp = cache_holder._end_caching()
        cached_dp = cached_dp.map(functools.partial(_wait_promise_fn, timeout))
        cached_dp = FileLister(cached_dp, recursive=True)

        if same_filepath_fn:
            filepath_fn = _filepath_fn

        todo_dp = datapipe
        if not skip_read:
            if "t" in mode:
                todo_dp = todo_dp.map(fn=_read_str, input_col=1)
            else:
                todo_dp = todo_dp.map(fn=_read_bytes, input_col=1)

        if filepath_fn is not None:
            todo_dp = todo_dp.map(fn=filepath_fn, input_col=0)

        # Extra hash check here when hash is provided.
        # And, raise Error if data returned from prior operations doesn't meet hash
        if _hash_dict is not None:
            todo_dp = todo_dp.check_hash(_hash_dict, _hash_type)

        todo_dp = todo_dp.save_to_disk(mode=mode)
        todo_dp = _FulfilledPromisesIterDataPipe(todo_dp)

        return cached_dp.concat(todo_dp)

    @staticmethod
    def _recursive_search(graph):
        for dp in graph.keys():
            # Find the closest CacheHolder
            if isinstance(dp, OnDiskCacheHolderIterDataPipe):
                return dp
        for dp in graph.values():
            res = EndOnDiskCacheHolderIterDataPipe._recursive_search(dp)
            if res is not None:
                return res
        return None
