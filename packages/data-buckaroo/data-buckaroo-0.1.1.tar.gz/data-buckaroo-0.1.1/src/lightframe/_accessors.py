# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC
from typing import (
    TYPE_CHECKING,
    Any,
    List,
    Union,
)

from lightframe.util import (
    _validate_slice_end,
    as_series_wrapper,
    get_ndim,
    to_date,
    to_datetime,
)

if TYPE_CHECKING:
    from lightframe.ndarray import SimpleNDArray


class _Accessor(ABC):
    def __init__(self, parent: SimpleNDArray):
        self._parent = parent


class _ILocIndexer(_Accessor):
    def _return_parent(self, cls, data, row_slicer, col_slicer=None):
        idx = self._parent.index[row_slicer]
        kwargs = {}
        if hasattr(self._parent, "columns"):
            if col_slicer is None:
                cols = self._parent.columns
            else:
                cols = self._parent.columns[col_slicer]
        else:
            cols = None
        if hasattr(cls, "columns"):
            kwargs["columns"] = cols
            kwargs["index"] = idx
        else:
            idx_dim = get_ndim(idx)
            col_dim = get_ndim(cols)
            if idx_dim == 0 and col_dim == 0:
                raise ValueError("cannot create a 0-dimensional frame")
            if idx_dim == 0 and col_dim == 1:
                kwargs["index"] = cols
                kwargs["name"] = idx
            else:
                kwargs["index"] = idx
                kwargs["name"] = cols
        return cls(data, **kwargs)

    def _get_rows(self, row_slicer: Union[int, slice]):
        r = self._parent.values[row_slicer]
        return r

    def _get_row_cols(self, row_slicer: Union[int, slice], col_slicer: Union[int, slice]):
        row_idx = (
            range(*row_slicer.indices(len(self._parent.values))) if isinstance(row_slicer, slice) else [row_slicer]
        )
        r = [self._parent.values[r][col_slicer] for r in row_idx]
        return r

    def __getitem__(self, key):
        # print(key)
        if isinstance(key, tuple) and len(key) == 1:
            key = key[0]
        if isinstance(key, tuple):
            if len(key) > self._parent.ndim:
                raise IndexError("too many indices")
            if all(isinstance(i, int) for i in key):
                # return a scalar
                r = self._parent.values
                for i in key:
                    r = r[i]
            else:
                r = self._get_row_cols(key[0], key[1])
        else:
            r = self._get_rows(key)

        kt = key if isinstance(key, tuple) else (key,)
        ndim = get_ndim(r)
        if ndim == 0:
            return r
        if ndim == self._parent.ndim:
            if len(r) == 1 and ndim == 2 and any(isinstance(i, int) for i in kt):
                return self._return_parent(self._parent.lower_dim_class, r[0], *kt)
            return self._return_parent(self._parent.__class__, r, *kt)
        if ndim == self._parent.ndim - 1:
            return self._return_parent(self._parent.lower_dim_class, r, *kt)
        raise NotImplementedError("indexing with {} dimensions".format(ndim))

    # def __setitem__(self, key, value):
    #     if isinstance(key, tuple) and len(key) == 1:
    #         key = key[0]
    #     if isinstance(key, tuple):
    #         if len(key) > 2 or len(key)> self._parent.ndim:
    #             raise IndexError("too many indices or not implemented")
    #         if all(isinstance(i, int) for i in key):
    #             # set a scalar
    #             self._parent._data[key[0]][key[1]] = value
    #         else:
    #             if isinstance(key[0],slice):
    #                 for r in range(*key[0].indices(len(self._parent.values))):
    #                     get_ndim(value)
    #
    #                     self._parent._data[r][key[1]] = value
    #             for r in range(len(self._parent.values[key[0]])):
    #                 self._parent._data[key[0]][r][key[1]] = value
    #             r = [self._parent.values[r][cols] for r in range(len(self._parent.values[rows]))]
    #             return r
    #             r = self._get_row_cols(key[0], key[1])
    #     else:
    #         self._parent._data[key] = value


class _LocIndexer(_ILocIndexer):
    def __getitem__(self, key):
        kt = key if isinstance(key, tuple) else (key,)
        if len(kt) > self._parent.ndim:
            raise IndexError("too many indices")
        idx: List[Any]
        new_indexers = []
        for i, idx in zip(kt, self._parent.axes):
            if isinstance(i, slice):
                start = _validate_slice_end(i.start, idx, "left")
                stop = _validate_slice_end(i.stop, idx[start:], "right")
                stop += start
                new_indexers.append(slice(start, stop, i.step))
            else:
                if i in idx:
                    new_indexers.append(idx.index(i))
                else:
                    raise ValueError("index {} is not in index".format(i))
        return super().__getitem__(tuple(new_indexers))


class _DtAccessor(_Accessor):
    @as_series_wrapper
    def to_pydatetime(self):
        return [to_datetime(a) for a in self._parent.values]

    @property
    @as_series_wrapper
    def date(self):
        return [to_date(a) for a in self._parent.values]


class _StrAccessor(_Accessor):
    @as_series_wrapper
    def encode(self, encoding="utf-8", errors="strict"):
        return [str(a).encode(encoding=encoding, errors=errors) for a in self._parent.values]
