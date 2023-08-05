# -*- coding: utf-8 -*-
from typing import Any, List

import tabulate

from lightframe._accessors import _DtAccessor, _StrAccessor
from lightframe.ndarray import NoLowerDimensionException, SimpleNDArray
from lightframe.repr import (
    MAX_ROWS,
    TRUNCATE_MAX_ROWS,
    _truncate_for_repr,
)
from lightframe.util import _to_list, _transpose


class LightSeries(SimpleNDArray):
    _data: List[Any]
    _name: Any
    _idx: List[Any]

    @property
    def str(self):
        return _StrAccessor(self)

    @property
    def dt(self):
        return _DtAccessor(self)

    def __init__(self, data, index=None, name=None):
        self._data = _to_list(data)
        if index is None:
            index = range(len(self._data))
        self._idx = _to_list(index)
        self._name = name

    @property
    def shape(self) -> tuple[int]:
        return (len(self._data),)

    @property
    def name(self):
        return self._name

    @property
    def ndim(self) -> int:
        return 1

    @property
    def lower_dim_class(self) -> type(SimpleNDArray):
        raise NoLowerDimensionException()

    def __repr__(self):
        if not self._data:
            return "LightSeries([])"
        tabulate.MIN_PADDING = 0
        fmt = tabulate.TableFormat(
            lineabove=None,
            linebelowheader=None,
            linebetweenrows=None,
            linebelow=None,
            headerrow=tabulate.DataRow("", "  ", ""),
            datarow=tabulate.DataRow("", "  ", ""),
            padding=0,
            with_header_hide=None,
        )

        rep = tabulate.tabulate(
            _transpose([_truncate_for_repr(self._data, MAX_ROWS, to_show=TRUNCATE_MAX_ROWS)]),
            showindex=_truncate_for_repr(
                self.index, MAX_ROWS, to_show=TRUNCATE_MAX_ROWS, filler="." * max(len(str(a)) for a in self._idx)
            ),
            missingval="<NA>",
            tablefmt=fmt,
            stralign="right",
            disable_numparse=True,
            numalign="right",
        )
        return rep + f"\nName: {self.name}"

    @property
    def axes(self) -> List[Any]:
        return [self.index]

    def __getitem__(self, key):
        return self.loc[key]

    def to_pandas(self):
        """Convert to Pandas Series"""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("Pandas is required for this operation")

        df = pd.Series(self.values, index=self.index, copy=True, name=self.name)
        return df

    def __iter__(self):
        return iter(self._data)

    def sort_values(self, ascending=True):
        r = sorted(zip(self._idx, self._data), key=lambda x: x[1], reverse=not ascending)
        return LightSeries([a[1] for a in r], [a[0] for a in r], self._name)

    def to_list(self):
        return self.values
