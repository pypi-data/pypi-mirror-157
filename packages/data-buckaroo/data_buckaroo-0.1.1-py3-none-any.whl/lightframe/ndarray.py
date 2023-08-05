# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List

from lightframe._accessors import _ILocIndexer, _LocIndexer


class NoLowerDimensionException(Exception):
    pass


class SimpleNDArray(ABC):
    _data: List[Any]
    _idx: List[Any]

    @property
    @abstractmethod
    def shape(self) -> tuple[int]:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def ndim(self) -> int:  # pragma: no cover
        pass

    @property
    def index(self) -> List[Any]:
        return self._idx

    @property
    def iloc(self):
        return _ILocIndexer(self)

    @property
    def loc(self):
        return _LocIndexer(self)

    @property
    @abstractmethod
    def lower_dim_class(self) -> type(SimpleNDArray):  # pragma: no cover
        pass

    @property
    @abstractmethod
    def axes(self) -> List[Any]:  # pragma: no cover
        pass

    @property
    def values(self) -> List[Any]:
        return self._data
