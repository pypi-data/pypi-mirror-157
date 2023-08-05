# -*- coding: utf-8 -*-
import csv
import io
from collections import defaultdict
from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    List,
    Optional,
)

import tabulate

from lightframe.ndarray import SimpleNDArray
from lightframe.repr import (
    MAX_COLS,
    MAX_ROWS,
    TRUNCATE_MAX_COLS,
    TRUNCATE_MAX_ROWS,
    _truncate_2d_for_repr,
    _truncate_for_repr,
)
from lightframe.series import LightSeries
from lightframe.util import (
    _to_list,
    _transpose,
    cast_to_type,
    to_datetime,
    wrap_func_in_none,
)


class LightFrame(SimpleNDArray):
    """
    row,column indexing
    """

    ndim = 2

    _data: List[List[Any]]
    _cols: List[Any]
    _pandas_dtypes: Optional[Dict[str, Any]]
    _idx: List[Any]

    def __init__(self, data, columns=None, index=None, **kwargs):
        self._pandas_dtypes = kwargs.get("pandas_dtypes", None)
        self._data = []
        max_len = 0
        to_extend = {}
        for r, row in enumerate(data):
            row = _to_list(row)
            self._data.append(row)
            max_len = max(max_len, len(row))
            if len(row) != max_len:
                to_extend[r] = max_len - len(row)
        for r, ext in to_extend.items():
            self._data[r].extend([None] * ext)

        if columns is None:
            columns = range(max_len)
        if index is None:
            index = range(len(self._data))
        columns = _to_list(columns)
        index = _to_list(index)
        if len(columns) < max_len:
            columns.extend(range(len(columns), max_len))
        if len(index) < len(self._data):
            index.extend(range(len(index), len(self._data)))
        self._cols = list(columns)
        self._idx = list(index)

    @property
    def lower_dim_class(self) -> type(SimpleNDArray):
        return LightSeries

    @property
    def shape(self) -> tuple[int, int]:
        """Returns the shape of the array.
        row, column order"""
        return len(self._idx), len(self._cols)

    def __repr__(self):
        if not self._data:
            return "Empty {class_name}\nColumns: {columns}\nIndex: {index}".format(
                class_name=self.__class__.__name__, columns=self._cols, index=self._idx
            )
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
            _transpose(
                _truncate_2d_for_repr(
                    _transpose(_truncate_2d_for_repr(self._data, MAX_ROWS, to_show=TRUNCATE_MAX_ROWS)),
                    MAX_COLS,
                    to_show=TRUNCATE_MAX_COLS,
                )
            ),
            headers=_truncate_for_repr(self._cols, MAX_COLS, to_show=TRUNCATE_MAX_COLS),
            showindex=_truncate_for_repr(
                self._idx, MAX_ROWS, to_show=TRUNCATE_MAX_ROWS, filler="." * max(len(str(a)) for a in self._idx)
            ),
            missingval="<NA>",
            tablefmt=fmt,
            stralign="right",
            disable_numparse=True,
            numalign="right",
        )
        return rep

    @property
    def columns(self):
        return self._cols

    @property
    def axes(self) -> List[Any]:
        return [self.index, self.columns]

    def to_pandas(self):
        """Convert to Pandas DataFrame"""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("Pandas is required for this operation")

        df = pd.DataFrame(self.values, columns=self.columns, index=self.index, copy=True)
        if self._pandas_dtypes is not None:
            for k, v in self._pandas_dtypes.items():
                df[k] = df[k].astype(v)
        return df

    @classmethod
    def read_csv(
        cls,
        buffer: io.TextIOWrapper,
        dtype: Optional[Dict[Hashable, Any]] = None,
        converters=None,
        parse_dates=None,
        quoting=csv.QUOTE_ALL,
        chunksize=None,
        **ignored_kwargs,
    ):
        r = cls._read_csv(buffer, dtype, converters, parse_dates, quoting, chunksize, **ignored_kwargs)
        if chunksize is None:
            return list(r)[0]
        return r

    @classmethod
    def _get_parser_funcs(cls, dtype: Optional[Dict[Hashable, Any]], converters, parse_dates, header: List[str]):

        pandas_dtypes = dtype.copy() if dtype else {}
        if parse_dates:
            for k in parse_dates:
                pandas_dtypes[k] = "datetime64[ns]"

        funcs: Dict[Hashable, Callable[[Any], Any]] = defaultdict(lambda: str)

        if parse_dates is not None:
            for date_col in parse_dates:
                funcs[date_col] = to_datetime
        if converters is not None:
            for k, v in converters.items():
                funcs[k] = wrap_func_in_none(v)
        if dtype is not None:
            for col, typ in dtype.items():
                funcs[col] = partial(cast_to_type, t=typ)
        nfuncs = tuple(funcs.get(col, str) for col in header)
        return nfuncs, pandas_dtypes

    @classmethod
    def _read_csv(  # noqa: C901
        cls,
        buffer: io.TextIOWrapper,
        dtype: Optional[Dict[Hashable, Any]] = None,
        converters=None,
        parse_dates=None,
        quoting=csv.QUOTE_ALL,
        chunksize=None,
        **ignored_kwargs,
    ):
        reader = csv.reader(buffer, quoting=quoting)

        header = next(reader)
        data = []
        nfuncs, pandas_dtypes = cls._get_parser_funcs(dtype, converters, parse_dates, header)
        idx = 0
        for row in reader:
            data.append([f(x) for f, x in zip(nfuncs, row)])
            if chunksize and len(data) >= chunksize:
                yield cls(data, columns=header, index=range(idx, idx + len(data)), pandas_dtypes=pandas_dtypes)
                idx += len(data)
                data = []
        if (data and idx > 0) or (idx == 0):
            # if there's a leftover chunk or this is the first chunk (even if it's empty), yield it
            yield cls(data, columns=header, index=range(idx, idx + len(data)), pandas_dtypes=pandas_dtypes)

    def __getitem__(self, key):
        return self.loc[:, key]

    def __setitem__(self, key, value):
        self.set_col(key, value)

    def set_col(self, col, values):
        if col not in self.columns:
            raise KeyError(col)
        col_idx = self.columns.index(col)
        for i, v in enumerate(values):
            self._data[i][col_idx] = v

    @property
    def T(self):
        return self.__class__(_transpose(self._data), columns=self.index, index=self.columns)
