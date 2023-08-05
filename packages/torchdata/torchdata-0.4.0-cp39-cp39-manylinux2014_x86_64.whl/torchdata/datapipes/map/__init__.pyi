# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.


from torch.utils.data.datapipes.map import Batcher, Concater, Mapper, SequenceWrapper, Shuffler, Zipper

from torchdata.datapipes.iter.util.converter import IterToMapConverterMapDataPipe as IterToMapConverter
from torchdata.datapipes.map.util.cacheholder import InMemoryCacheHolderMapDataPipe as InMemoryCacheHolder
from torchdata.datapipes.map.util.unzipper import UnZipperMapDataPipe as UnZipper

__all__ = [
    "Batcher",
    "Concater",
    "InMemoryCacheHolder",
    "IterToMapConverter",
    "MapDataPipe",
    "Mapper",
    "SequenceWrapper",
    "Shuffler",
    "UnZipper",
    "Zipper",
]

# Please keep this list sorted
assert __all__ == sorted(__all__)

########################################################################################################################
# The part below is generated by parsing through the Python files where MapDataPipes are defined.
# This base template ("__init__.pyi.in") is generated from mypy stubgen with minimal editing for code injection
# The output file will be "__init__.pyi". The generation function is called by "setup.py".
# Note that, for mypy, .pyi file takes precedent over .py file, such that we must define the interface for other
# classes/objects here, even though we are not injecting extra code into them at the moment.

from torch.utils.data import DataChunk, Dataset
from torch.utils.data.datapipes._typing import _DataPipeMeta

from typing import Any, Callable, Dict, List, Optional, Sequence, TypeVar, Union

T_co = TypeVar('T_co', covariant=True)
T = TypeVar('T')
UNTRACABLE_DATAFRAME_PIPES: Any

class MapDataPipe(Dataset[T_co], metaclass=_DataPipeMeta):
    functions: Dict[str, Callable] = ...
    def __getattr__(self, attribute_name: Any): ...
    @classmethod
    def register_function(cls, function_name: Any, function: Any) -> None: ...
    @classmethod
    def register_datapipe_as_function(cls, function_name: Any, cls_to_register: Any): ...
    # Functional form of 'BatcherMapDataPipe'
    def batch(self, batch_size: int, drop_last: bool = False, wrapper_class=DataChunk) -> MapDataPipe: ...
    # Functional form of 'ConcaterMapDataPipe'
    def concat(self, *datapipes: MapDataPipe) -> MapDataPipe: ...
    # Functional form of 'MapperMapDataPipe'
    def map(self, fn: Callable= ...) -> MapDataPipe: ...
    # Functional form of 'ShufflerMapDataPipe'
    def shuffle(self, *, indices: Optional[List] = None) -> MapDataPipe: ...
    # Functional form of 'ZipperMapDataPipe'
    def zip(self, *datapipes: MapDataPipe[T_co]) -> MapDataPipe: ...
    # Functional form of 'InMemoryCacheHolderMapDataPipe'
    def in_memory_cache(self) -> MapDataPipe: ...
    # Functional form of 'MapToIterConverterIterDataPipe'
    def to_iter_datapipe(self, indices: Optional[List] = None) -> MapDataPipe: ...
    # Functional form of 'UnZipperMapDataPipe'
    def unzip(self, sequence_length: int, columns_to_skip: Optional[Sequence[int]] = None) -> List[MapDataPipe]: ...
