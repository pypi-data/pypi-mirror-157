# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime
import functools
from collections.abc import Iterable
from decimal import Decimal

from dateutil.parser import isoparse, parse


def _transpose(data):
    return list(zip(*data))


def wrap_func_in_none(func, na_values=("", "NaN")):
    @functools.wraps(func)
    def wrapper(x, *args, **kwargs):
        if x is None or x in na_values:
            return None
        return func(x, *args, **kwargs)

    return wrapper


@wrap_func_in_none
def cast_to_type(x, t):
    t = t.lower()
    if t.startswith("int"):
        return int(x)
    if t.startswith("float"):
        return float(x)
    if t.startswith("bool"):
        return str(x).lower() in ["true", "1", "t", "y", "yes", "on"]
    if t.startswith("str"):
        return str(x)
    if t == "date":
        return isoparse(x).date()
    if t.startswith("datetime"):
        return isoparse(x)
    if t == "decimal":
        return Decimal(x)
    if t == "bytes":
        return bytes(x)
    raise ValueError(f"Unknown type {t}")


def _iterable(arg):
    return isinstance(arg, Iterable) and not isinstance(arg, (str, bytes, bytearray))


def _to_list(arg):
    if _iterable(arg):
        return list(arg)
    return [arg]


@wrap_func_in_none
def to_date(obj):
    if isinstance(obj, datetime.datetime):
        return obj.date()
    if isinstance(obj, datetime.date):
        return obj
    if isinstance(obj, str):
        return parse(obj).date()

    raise TypeError(f"cannot convert {type(obj)} to a date")


@wrap_func_in_none
def to_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj
    if isinstance(obj, datetime.date):
        return datetime.datetime.combine(obj, datetime.time())
    if isinstance(obj, str):
        return parse(obj)
    raise TypeError(f"cannot convert {type(obj)} to a datetime")


def as_series_wrapper(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        from lightframe.series import LightSeries

        result = func(self, *args, **kwargs)
        if not _iterable(result):
            return result
        return LightSeries(result, index=self._parent.index, name=self._parent.name)

    return wrapper


def get_ndim(obj, ndim=0):
    maxdim = ndim
    if isinstance(obj, list):
        maxdim += 1
        for i in obj:
            maxdim = max(maxdim, get_ndim(i, ndim + 1))
        return maxdim
    return maxdim


def _validate_slice_end(value, idx, end):
    if value is None:
        if end == "left":
            return 0
        if end == "right":
            return len(idx)
    if value in idx:
        return idx.index(value)
    raise ValueError("index {} is not in index".format(value))
