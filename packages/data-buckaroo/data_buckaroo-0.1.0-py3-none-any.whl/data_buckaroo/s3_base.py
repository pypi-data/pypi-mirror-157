# -*- coding: utf-8 -*-
import datetime
import fnmatch
import logging
import pprint
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import botocore
import botocore.client
import botocore.exceptions
from boto3 import Session

from lightframe.frame import LightFrame

from . import _exceptions
from .s3_object_base import S3ObjectBase
from .utils import (
    CallableReturningDataFrame,
    ChunkedDataFrameType,
    DataFrameType,
    DataReturnType,
    _prefix_cleanup,
    _validate_datetimes,
    get_botocore_valid_kwargs,
    parse_path,
    try_it,
)

_logger: logging.Logger = logging.getLogger(__name__)


class S3Base:
    def __init__(self, session: Session, client_s3: botocore.client.BaseClient):
        self.session = session
        self.client_s3 = client_s3

    def read_csv(
        self,
        path: Union[str, List[str]],
        # path_suffix: Union[str, List[str], None] = None,
        # path_ignore_suffix: Union[str, List[str], None] = None,
        # version_id: Optional[Union[str, Dict[str, str]]] = None,
        # ignore_empty: bool = True,
        # last_modified_begin: Optional[datetime.datetime] = None,
        # last_modified_end: Optional[datetime.datetime] = None,
        # s3_additional_kwargs: Optional[Dict[str, Any]] = None,
        # dataset: bool = False,
        # partition_filter: Optional[Callable[[Dict[str, str]], bool]] = None,
        chunksize: Optional[Union[int, bool]] = None,
        **parser_kwargs: Any,
        # dtype=query_metadata.dtype,
        # parse_dates=query_metadata.parse_timestamps,
        # converters=query_metadata.converters,
        # quoting=csv.QUOTE_ALL,
        # keep_default_na=False,
        # na_values=["", "NaN"],
        # skip_blank_lines=False,
    ) -> DataReturnType:
        if "parser_kwargs" in parser_kwargs:
            raise _exceptions.InvalidArgument(
                "You can NOT pass `parser_kwargs` explicit, just add valid "
                "Pandas arguments in the function call and Wrangler will accept it."
                "e.g. wr.s3.read_csv('s3://bucket/prefix/', sep='|', skip_blank_lines=True)"
            )
        ignore_index: bool = "index_col" not in parser_kwargs
        return self._read_text(
            parser_func=LightFrame.read_csv,
            path=path,
            ignore_index=ignore_index,
            chunksize=chunksize,
            **parser_kwargs,
        )

    def _read_text_chunked(
        self,
        paths: List[str],
        parser_func: CallableReturningDataFrame,
        # path_root: Optional[str],
        parser_kwargs: Dict[str, Any],
        # s3_additional_kwargs: Optional[Dict[str, str]],
        # dataset: bool,
        chunksize: Union[int, bool],
        # version_ids: Optional[Dict[str, str]] = None,
    ) -> ChunkedDataFrameType:
        for path in paths:
            _logger.debug("path: %s", path)
            # mode, encoding, newline = _get_read_details(path=path, parser_kwargs=parser_kwargs)
            with S3ObjectBase.open_s3_object(
                s3_base=self,
                path=path,
                # version_id=version_ids.get(path) if version_ids else None,
                mode="r",
                s3_block_size=10_485_760,  # 10 MB (10 * 2**20)
                encoding="utf-8",
                # s3_additional_kwargs=s3_additional_kwargs,
                newline=None,
            ) as f:
                # noinspection PyUnresolvedReferences
                reader: ChunkedDataFrameType = parser_func(f, chunksize=chunksize, **parser_kwargs)
                for df in reader:
                    yield df

    def _read_text_file(
        self,
        path: str,
        # version_id: Optional[str],
        parser_func: CallableReturningDataFrame,
        # path_root: Optional[str],
        parser_kwargs: Dict[str, Any],
        # s3_additional_kwargs: Optional[Dict[str, str]],
        # dataset: bool,
    ) -> DataFrameType:
        try:
            with S3ObjectBase.open_s3_object(
                s3_base=self,
                path=path,
                # version_id=version_id,
                mode="r",
                s3_block_size=-1,  # One shot download
                encoding="utf-8",
                # s3_additional_kwargs=s3_additional_kwargs,
                newline=None,
            ) as f:
                df: DataFrameType = parser_func(f, **parser_kwargs)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise _exceptions.NoFilesFound(f"No files Found on: {path}.")
            raise e
        return df

    def _read_text(
        self,
        parser_func: CallableReturningDataFrame,
        path: Union[str, List[str]],
        ignore_index: bool,
        chunksize: Optional[Union[int, bool]] = None,
        **parser_kwargs: Any,
    ) -> DataReturnType:
        if "iterator" in parser_kwargs:
            raise _exceptions.InvalidArgument("Please, use the chunksize argument instead of iterator.")

        paths: List[str] = self.path2list(
            path=path,
            ignore_suffix=["/_SUCCESS"],
            ignore_empty=True,
            last_modified_begin=None,
            last_modified_end=None,
            s3_additional_kwargs=None,
        )
        if len(paths) < 1:
            raise _exceptions.NoFilesFound(f"No files Found on: {path}.")
        _logger.debug("paths:\n%s", paths)

        args: Dict[str, Any] = {
            "parser_func": parser_func,
            # "boto3_session": self.session,
            # "dataset": dataset,
            # "path_root": path_root,
            "parser_kwargs": parser_kwargs,
            # "s3_additional_kwargs": s3_additional_kwargs,
        }
        _logger.debug("args:\n%s", pprint.pformat(args))
        ret: DataReturnType
        if chunksize is not None:
            ret = self._read_text_chunked(
                paths=paths,
                # version_ids=version_id if isinstance(version_id, dict) else None,
                chunksize=chunksize,
                **args,
            )
        elif len(paths) == 1:
            ret = self._read_text_file(
                path=paths[0],
                # version_id=version_id[paths[0]] if isinstance(version_id, dict) else version_id,
                **args,
            )
        else:
            raise NotImplementedError("Multiple files are not supported yet.")
            # ret = _union(
            #     dfs=_read_dfs_from_multiple_paths(
            #         read_func=self._read_text_file,
            #         paths=paths,
            #         # version_ids=version_id if isinstance(version_id, dict) else None,
            #         kwargs=args,
            #     ),
            #     ignore_index=ignore_index,
            # )
        return ret

    def _list_objects(  # noqa: C901  pylint: disable=too-many-branches
        self,
        path: str,
        s3_additional_kwargs: Optional[Dict[str, Any]],
        delimiter: Optional[str] = None,
        suffix: Union[str, List[str], None] = None,
        ignore_suffix: Union[str, List[str], None] = None,
        last_modified_begin: Optional[datetime.datetime] = None,
        last_modified_end: Optional[datetime.datetime] = None,
        ignore_empty: bool = False,
    ) -> Iterator[List[str]]:
        bucket: str
        prefix_original: str
        bucket, prefix_original = parse_path(path=path)
        prefix: str = _prefix_cleanup(prefix=prefix_original)
        _suffix: Union[List[str], None] = [suffix] if isinstance(suffix, str) else suffix
        _ignore_suffix: Union[List[str], None] = [ignore_suffix] if isinstance(ignore_suffix, str) else ignore_suffix
        default_pagination: Dict[str, int] = {"PageSize": 1000}
        extra_kwargs: Dict[str, Any] = {"PaginationConfig": default_pagination}
        if s3_additional_kwargs:
            extra_kwargs = get_botocore_valid_kwargs(
                function_name="list_objects_v2",
                s3_additional_kwargs=s3_additional_kwargs,
            )
            extra_kwargs["PaginationConfig"] = (
                s3_additional_kwargs["PaginationConfig"]
                if "PaginationConfig" in s3_additional_kwargs
                else default_pagination
            )

        paginator = self.client_s3.get_paginator("list_objects_v2")
        args: Dict[str, Any] = {"Bucket": bucket, "Prefix": prefix, **extra_kwargs}
        if delimiter is not None:
            args["Delimiter"] = delimiter
        _logger.debug("args: %s", args)
        response_iterator = paginator.paginate(**args)
        paths: List[str] = []
        _validate_datetimes(last_modified_begin=last_modified_begin, last_modified_end=last_modified_end)

        for page in response_iterator:  # pylint: disable=too-many-nested-blocks
            if delimiter is None:
                contents: Optional[List[Dict[str, Any]]] = page.get("Contents")
                if contents is not None:
                    for content in contents:
                        key: str = content["Key"]
                        if ignore_empty and content.get("Size", 0) == 0:
                            _logger.debug("Skipping empty file: %s", f"s3://{bucket}/{key}")
                        elif (content is not None) and ("Key" in content):
                            if (_suffix is None) or key.endswith(tuple(_suffix)):
                                if last_modified_begin is not None:
                                    if content["LastModified"] < last_modified_begin:
                                        continue
                                if last_modified_end is not None:
                                    if content["LastModified"] > last_modified_end:
                                        continue
                                paths.append(f"s3://{bucket}/{key}")
            else:
                prefixes: Optional[List[Optional[Dict[str, str]]]] = page.get("CommonPrefixes")
                if prefixes is not None:
                    for pfx in prefixes:
                        if (pfx is not None) and ("Prefix" in pfx):
                            key = pfx["Prefix"]
                            paths.append(f"s3://{bucket}/{key}")

            if prefix != prefix_original:
                paths = fnmatch.filter(paths, path)

            if _ignore_suffix is not None:
                paths = [p for p in paths if p.endswith(tuple(_ignore_suffix)) is False]

            if paths:
                yield paths
            paths = []

    def list_objects(
        self,
        path: str,
        suffix: Union[str, List[str], None] = None,
        ignore_suffix: Union[str, List[str], None] = None,
        last_modified_begin: Optional[datetime.datetime] = None,
        last_modified_end: Optional[datetime.datetime] = None,
        ignore_empty: bool = False,
        chunked: bool = False,
        s3_additional_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Union[List[str], Iterator[List[str]]]:
        # On top of user provided ignore_suffix input, add "/"
        ignore_suffix_acc = set("/")
        if isinstance(ignore_suffix, str):
            ignore_suffix_acc.add(ignore_suffix)
        elif isinstance(ignore_suffix, list):
            ignore_suffix_acc.update(ignore_suffix)

        result_iterator = self._list_objects(
            path=path,
            delimiter=None,
            suffix=suffix,
            ignore_suffix=list(ignore_suffix_acc),
            last_modified_begin=last_modified_begin,
            last_modified_end=last_modified_end,
            ignore_empty=ignore_empty,
            s3_additional_kwargs=s3_additional_kwargs,
        )
        if chunked:
            return result_iterator
        return [path for paths in result_iterator for path in paths]

    def describe_objects(
        self,
        path: Union[str, List[str]],
        version_id: Optional[Union[str, Dict[str, str]]] = None,
        last_modified_begin: Optional[datetime.datetime] = None,
        last_modified_end: Optional[datetime.datetime] = None,
        s3_additional_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        paths: List[str] = self.path2list(
            path=path,
            last_modified_begin=last_modified_begin,
            last_modified_end=last_modified_end,
            s3_additional_kwargs=s3_additional_kwargs,
        )
        if len(paths) < 1:
            return {}
        resp_list: List[Tuple[str, Dict[str, Any]]]
        if len(paths) == 1:
            resp_list = [
                self._describe_object(
                    path=paths[0],
                    version_id=version_id.get(paths[0]) if isinstance(version_id, dict) else version_id,
                    s3_additional_kwargs=s3_additional_kwargs,
                )
            ]
        else:
            resp_list = [
                self._describe_object(
                    path=p,
                    version_id=version_id.get(p) if isinstance(version_id, dict) else version_id,
                    s3_additional_kwargs=s3_additional_kwargs,
                )
                for p in paths
            ]

        desc_dict: Dict[str, Dict[str, Any]] = dict(resp_list)
        return desc_dict

    def size_objects(
        self,
        path: Union[str, List[str]],
        version_id: Optional[Union[str, Dict[str, str]]] = None,
        s3_additional_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Optional[int]]:
        desc_list: Dict[str, Dict[str, Any]] = self.describe_objects(
            path=path,
            version_id=version_id,
            s3_additional_kwargs=s3_additional_kwargs,
        )
        size_dict: Dict[str, Optional[int]] = {k: d.get("ContentLength", None) for k, d in desc_list.items()}
        return size_dict

    def path2list(
        self,
        path: Union[str, Sequence[str]],
        s3_additional_kwargs: Optional[Dict[str, Any]],
        last_modified_begin: Optional[datetime.datetime] = None,
        last_modified_end: Optional[datetime.datetime] = None,
        suffix: Union[str, List[str], None] = None,
        ignore_suffix: Union[str, List[str], None] = None,
        ignore_empty: bool = False,
    ) -> List[str]:
        """Convert Amazon S3 path to list of objects."""
        _suffix: Optional[List[str]] = [suffix] if isinstance(suffix, str) else suffix
        _ignore_suffix: Optional[List[str]] = [ignore_suffix] if isinstance(ignore_suffix, str) else ignore_suffix
        if isinstance(path, str):  # prefix
            paths: List[str] = self.list_objects(  # type: ignore
                path=path,
                suffix=_suffix,
                ignore_suffix=_ignore_suffix,
                last_modified_begin=last_modified_begin,
                last_modified_end=last_modified_end,
                ignore_empty=ignore_empty,
                s3_additional_kwargs=s3_additional_kwargs,
            )
        elif isinstance(path, list):
            if last_modified_begin or last_modified_end:
                raise _exceptions.InvalidArgumentCombination(
                    "Specify a list of files or (last_modified_begin and last_modified_end)"
                )
            paths = path if _suffix is None else [x for x in path if x.endswith(tuple(_suffix))]
            paths = path if _ignore_suffix is None else [x for x in paths if x.endswith(tuple(_ignore_suffix)) is False]
        else:
            raise _exceptions.InvalidArgumentType(
                f"{type(path)} is not a valid path type. Please, use str or List[str]."
            )
        return paths

    def _describe_object(
        self,
        path: str,
        s3_additional_kwargs: Optional[Dict[str, Any]],
        version_id: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:

        bucket: str
        key: str
        bucket, key = parse_path(path=path)
        if s3_additional_kwargs:
            extra_kwargs: Dict[str, Any] = get_botocore_valid_kwargs(
                function_name="head_object", s3_additional_kwargs=s3_additional_kwargs
            )
        else:
            extra_kwargs = {}
        desc: Dict[str, Any]
        if version_id:
            extra_kwargs["VersionId"] = version_id
        desc = try_it(
            f=self.client_s3.head_object,
            ex=self.client_s3.exceptions.NoSuchKey,
            Bucket=bucket,
            Key=key,
            **extra_kwargs,
        )
        return path, desc
