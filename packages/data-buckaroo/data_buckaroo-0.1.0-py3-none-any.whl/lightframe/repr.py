# -*- coding: utf-8 -*-
from __future__ import annotations

MAX_ROWS = 60
MAX_COLS = 20
TRUNCATE_MAX_COLS = 6
TRUNCATE_MAX_ROWS = 10


def _truncate_for_repr(data, n=60, filler="...", to_show=6):
    if len(data) > n:
        return data[: to_show // 2] + [filler] + data[-to_show // 2 :]
    return data


def _truncate_2d_for_repr(data, n=60, filler="...", to_show=10):
    if len(data) > n:
        return data[: to_show // 2] + [[filler] * len(data[0])] + data[-to_show // 2 :]
    return data
