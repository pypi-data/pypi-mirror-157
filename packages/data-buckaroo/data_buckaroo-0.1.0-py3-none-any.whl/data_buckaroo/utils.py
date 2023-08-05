# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import datetime
import logging
import os
import random
import time
import warnings
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)

import boto3
import botocore.config
from botocore.loaders import Loader
from botocore.model import ServiceModel

try:
    # import pandas as pd

    PANDAS_ENABLED = False
except ImportError:
    PANDAS_ENABLED = False

from lightframe.frame import LightFrame

from . import _exceptions
from .__metadata__ import __version__

_logger: logging.Logger = logging.getLogger(__name__)

DataFrameType = Union["pd.DataFrame", LightFrame]
ChunkedDataFrameType = Iterator[DataFrameType]
DataReturnType = Union[DataFrameType, ChunkedDataFrameType]
CallableReturningDataFrame = Callable[..., DataFrameType]


def get_botocore_valid_kwargs(function_name: str, s3_additional_kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Filter and keep only the valid botocore key arguments."""
    s3_operation_model = _S3_SERVICE_MODEL.operation_model(_snake_to_camel_case(function_name))
    allowed_kwargs = s3_operation_model.input_shape.members.keys()  # pylint: disable=E1101
    return {k: v for k, v in s3_additional_kwargs.items() if k in allowed_kwargs}


def parse_path(path: str) -> Tuple[str, str]:
    """Split a full S3 path in bucket and key strings.

    's3://bucket/key' -> ('bucket', 'key')

    Parameters
    ----------
    path : str
    Returns
    -------
    Tuple[str, str]

    """
    if path.startswith("s3://") is False:
        raise _exceptions.InvalidArgumentValue(f"'{path}' is not a valid path. It MUST start with 's3://'")
    parts = path.replace("s3://", "").replace(":accesspoint/", ":accesspoint:").split("/", 1)
    bucket: str = parts[0]
    if "/" in bucket:
        raise _exceptions.InvalidArgumentValue(f"'{bucket}' is not a valid bucket name.")
    key: str = ""
    if len(parts) == 2:
        key = key if parts[1] is None else parts[1]
    return bucket, key


def try_it(
    f: Callable[..., Any],
    ex: Any,
    ex_code: Optional[str] = None,
    base: float = 1.0,
    max_num_tries: int = 3,
    **kwargs: Any,
) -> Any:
    """Run function with decorrelated Jitter.

    Reference: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    """
    delay: float = base
    for i in range(max_num_tries):
        try:
            return f(**kwargs)
        except ex as exception:
            if ex_code is not None and hasattr(exception, "response"):
                if exception.response["Error"]["Code"] != ex_code:
                    raise
            if i == (max_num_tries - 1):
                raise
            delay = random.uniform(base, delay * 3)
            _logger.error(
                "Retrying %s | Fail number %s/%s | Exception: %s",
                f,
                i + 1,
                max_num_tries,
                exception,
            )
            time.sleep(delay)
    raise RuntimeError()


def _prefix_cleanup(prefix: str) -> str:
    for n, c in enumerate(prefix):
        if c in ["*", "?", "["]:
            return prefix[:n]
    return prefix


def _validate_datetimes(
    last_modified_begin: Optional[datetime.datetime] = None,
    last_modified_end: Optional[datetime.datetime] = None,
) -> None:
    if (last_modified_begin is not None) and (last_modified_begin.tzinfo is None):
        raise _exceptions.InvalidArgumentValue("Timezone is not defined for last_modified_begin.")
    if (last_modified_end is not None) and (last_modified_end.tzinfo is None):
        raise _exceptions.InvalidArgumentValue("Timezone is not defined for last_modified_end.")
    if (last_modified_begin is not None) and (last_modified_end is not None):
        if last_modified_begin > last_modified_end:
            raise _exceptions.InvalidArgumentValue("last_modified_begin is bigger than last_modified_end.")


_QUERY_FINAL_STATES: List[str] = ["FAILED", "SUCCEEDED", "CANCELLED"]
_QUERY_WAIT_POLLING_DELAY: float = 0.25  # SECONDS
Boto3PrimitivesType = Dict[str, Optional[str]]


class _QueryMetadata(NamedTuple):
    execution_id: str
    dtype: Dict[str, str]
    parse_timestamps: List[str]
    parse_dates: List[str]
    converters: Dict[str, Any]
    binaries: List[str]
    output_location: Optional[str]
    manifest_location: Optional[str]
    raw_payload: Dict[str, Any]


class _WorkGroupConfig(NamedTuple):
    enforced: bool
    s3_output: Optional[str]
    encryption: Optional[str]
    kms_key: Optional[str]


def _add_query_metadata_generator(dfs: ChunkedDataFrameType, query_metadata: _QueryMetadata) -> ChunkedDataFrameType:
    """Add Query Execution metadata to every DF in iterator."""
    for df in dfs:
        df = _apply_query_metadata(df=df, query_metadata=query_metadata)
        yield df


def _apply_query_metadata(df: DataFrameType, query_metadata: _QueryMetadata) -> DataFrameType:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        df.query_metadata = query_metadata.raw_payload
    return df


def _empty_dataframe_response(
    chunked: bool, query_metadata: _QueryMetadata
) -> Union[DataFrameType, Generator[None, None, None]]:
    """Generate an empty dataframe response."""
    if chunked is False:
        if PANDAS_ENABLED:
            df = pd.DataFrame()
        else:
            df = LightFrame()
        df = _apply_query_metadata(df=df, query_metadata=query_metadata)
        return df
    return empty_generator()


def _fix_csv_types(df: DataFrameType, parse_dates: List[str], binaries: List[str]) -> DataFrameType:
    """Apply data types cast to a Pandas DataFrames."""
    if len(df.index) > 0:
        if isinstance(df, LightFrame):
            for col in parse_dates:
                df[col] = df[col].dt.date
            for col in binaries:
                df[col] = df[col].str.encode(encoding="utf-8")
        else:
            for col in parse_dates:
                df[col] = df[col].dt.date.replace(to_replace={pd.NaT: None})
            for col in binaries:
                df[col] = df[col].str.encode(encoding="utf-8")
    return df


def _fix_csv_types_generator(
    dfs: ChunkedDataFrameType, parse_dates: List[str], binaries: List[str]
) -> ChunkedDataFrameType:
    """Apply data types cast to a Pandas DataFrames Generator."""
    for df in dfs:
        yield _fix_csv_types(df=df, parse_dates=parse_dates, binaries=binaries)


#
# def _read_dfs_from_multiple_paths(
#     read_func: CallableReturningDataFrame,
#     paths: List[str],
#     # version_ids: Optional[Dict[str, str]],
#     kwargs: Dict[str, Any],
# ) -> List[DataFrameType]:
#     return [
#         read_func(
#             path,
#             **kwargs,
#         )
#         for path in paths
#     ]


# def _union(dfs: List[DataFrameType], ignore_index: Optional[bool]) -> DataFrameType:
#     if ignore_index is None:
#         ignore_index = False
#         for df in dfs:
#             if hasattr(df, "_awswrangler_ignore_index"):
#                 # noinspection PyProtectedMember
#                 if df._awswrangler_ignore_index is True:  # pylint: disable=protected-access
#                     ignore_index = True
#                     break
#     cats: Tuple[Set[str], ...] = tuple(set(df.select_dtypes(include="category").columns) for df in dfs)
#     for col in set.intersection(*cats):
#         cat = union_categoricals([df[col] for df in dfs])
#         for df in dfs:
#             df[col] = pd.Categorical(df[col].values, categories=cat.categories)
#     return pd.concat(objs=dfs, sort=False, copy=False, ignore_index=ignore_index)


def athena2pandas(  # noqa: C901  pylint: disable=too-many-branches,too-many-return-statements
    dtype: str,
) -> str:
    """Athena to Pandas data types conversion."""
    dtype = dtype.lower()
    if dtype == "tinyint":
        return "Int8"
    if dtype == "smallint":
        return "Int16"
    if dtype in ("int", "integer"):
        return "Int32"
    if dtype == "bigint":
        return "Int64"
    if dtype in ("float", "real"):
        return "float32"
    if dtype == "double":
        return "float64"
    if dtype == "boolean":
        return "boolean"
    if (dtype == "string") or dtype.startswith("char") or dtype.startswith("varchar"):
        return "string"
    if dtype in ("timestamp", "timestamp with time zone"):
        return "datetime64"
    if dtype == "date":
        return "date"
    if dtype.startswith("decimal"):
        return "decimal"
    if dtype in ("binary", "varbinary"):
        return "bytes"
    raise _exceptions.UnsupportedType(f"Unsupported Athena type: {dtype}")


def boto3_from_primitives(
    primitives: Optional[Boto3PrimitivesType] = None,
) -> boto3.Session:
    """Convert Python primitives to Boto3 Session."""
    if primitives is None:
        return ensure_session()
    _primitives: Boto3PrimitivesType = copy.deepcopy(primitives)
    profile_name: Optional[str] = _primitives.get("profile_name", None)
    _primitives["profile_name"] = None if profile_name in (None, "default") else profile_name
    args: Dict[str, str] = {k: v for k, v in _primitives.items() if v is not None}
    return boto3.Session(**args)


def default_botocore_config() -> botocore.config.Config:
    """Botocore configuration."""
    retries_config: Dict[str, Union[str, int]] = {
        "max_attempts": int(os.getenv("AWS_MAX_ATTEMPTS", "5")),
    }
    mode: Optional[str] = os.getenv("AWS_RETRY_MODE")
    if mode:
        retries_config["mode"] = mode
    return botocore.config.Config(
        retries=retries_config,
        connect_timeout=10,
        max_pool_connections=10,
        user_agent_extra=f"data_buckaroo/{__version__}",
    )


def empty_generator() -> Generator[None, None, None]:
    """Empty Generator."""
    yield from ()


def ensure_session(session: Union[None, boto3.Session, Boto3PrimitivesType] = None) -> boto3.Session:
    """Ensure that a valid boto3.Session will be returned."""
    if isinstance(session, dict):  # Primitives received
        return boto3_from_primitives(primitives=session)
    if session is not None:
        return session
    # Ensure the boto3's default session is used so that its parameters can be
    # set via boto3.setup_default_session()
    if boto3.DEFAULT_SESSION is not None:
        return boto3.DEFAULT_SESSION
    return boto3.Session()


_BOTOCORE_LOADER = Loader()
_S3_JSON_MODEL = _BOTOCORE_LOADER.load_service_model(service_name="s3", type_name="service-2")
_S3_SERVICE_MODEL = ServiceModel(_S3_JSON_MODEL, service_name="s3")


def _snake_to_camel_case(s: str) -> str:
    return "".join(c.title() for c in s.split("_"))
