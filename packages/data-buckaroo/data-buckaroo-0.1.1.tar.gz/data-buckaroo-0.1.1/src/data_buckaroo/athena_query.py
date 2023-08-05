# -*- coding: utf-8 -*-
import csv
import logging
import pprint
import sys
import time
from decimal import Decimal
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    cast,
)

import boto3
import botocore.config
import botocore.exceptions

from . import _exceptions
from .s3_base import S3Base
from .utils import (
    _QUERY_FINAL_STATES,
    _QUERY_WAIT_POLLING_DELAY,
    Boto3PrimitivesType,
    DataReturnType,
    _add_query_metadata_generator,
    _apply_query_metadata,
    _empty_dataframe_response,
    _fix_csv_types,
    _fix_csv_types_generator,
    _QueryMetadata,
    _WorkGroupConfig,
    athena2pandas,
    default_botocore_config,
    ensure_session,
    try_it,
)

_logger: logging.Logger = logging.getLogger(__name__)


class AthenaQuery:
    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        database: str,
        categories: Optional[List[str]] = None,
        chunksize: Optional[Union[int, bool]] = None,
        s3_output: Optional[str] = None,
        workgroup: Optional[str] = None,
        encryption: Optional[str] = None,
        data_source: Optional[str] = None,
        kms_key: Optional[str] = None,
        session: Union[None, boto3.Session, Boto3PrimitivesType] = None,
    ):

        self.session = ensure_session(session=session)

        self.database = database
        self.categories = categories
        self.chunksize = sys.maxsize if chunksize is True else chunksize
        self.s3_output = s3_output
        self.workgroup = workgroup
        self.encryption = encryption
        self.kms_key = kms_key
        self.data_source = data_source

        self.client_athena = self._client(service_name="athena")
        self.client_s3 = self._client(service_name="s3")
        self.s3_base = S3Base(session=self.session, client_s3=self.client_s3)

        self.wg_config = self._get_workgroup_config()

    def read_sql_query(
        self,
        sql: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> DataReturnType:

        if params is None:
            params = {}
        for key, value in params.items():
            sql = sql.replace(f":{key};", str(value))

        return self._resolve_query_without_cache(
            sql=sql,
        )

    def _resolve_query_without_cache(
        self,
        sql: str,
    ) -> DataReturnType:
        _logger.debug("sql: %s", sql)
        query_id: str = self._start_query_execution(sql=sql)
        _logger.debug("query_id: %s", query_id)
        query_metadata: _QueryMetadata = self._get_query_metadata(
            query_execution_id=query_id,
        )
        return self._fetch_csv_result(
            query_metadata=query_metadata,
        )

    def _start_query_execution(
        self,
        sql: str,
    ) -> str:
        args: Dict[str, Any] = {"QueryString": sql}

        # s3_output
        args["ResultConfiguration"] = {"OutputLocation": self._get_s3_output()}

        # encryption
        if self.wg_config.enforced is True:
            if self.wg_config.encryption is not None:
                args["ResultConfiguration"]["EncryptionConfiguration"] = {"EncryptionOption": self.wg_config.encryption}
                if self.wg_config.kms_key is not None:
                    args["ResultConfiguration"]["EncryptionConfiguration"]["KmsKey"] = self.wg_config.kms_key
        else:
            if self.encryption is not None:
                args["ResultConfiguration"]["EncryptionConfiguration"] = {"EncryptionOption": self.encryption}
                if self.kms_key is not None:
                    args["ResultConfiguration"]["EncryptionConfiguration"]["KmsKey"] = self.kms_key

        # database
        if self.database is not None:
            args["QueryExecutionContext"] = {"Database": self.database}
            if self.data_source is not None:
                args["QueryExecutionContext"]["Catalog"] = self.data_source

        # workgroup
        if self.workgroup is not None:
            args["WorkGroup"] = self.workgroup

        _logger.debug("args: \n%s", pprint.pformat(args))
        response: Dict[str, Any] = try_it(
            f=self.client_athena.start_query_execution,
            ex=botocore.exceptions.ClientError,
            ex_code="ThrottlingException",
            max_num_tries=5,
            **args,
        )
        return cast(str, response["QueryExecutionId"])

    def _get_s3_output(self) -> str:
        if self.wg_config.enforced and self.wg_config.s3_output is not None:
            return self.wg_config.s3_output
        if self.s3_output is not None:
            return self.s3_output
        if self.wg_config.s3_output is not None:
            return self.wg_config.s3_output
        raise _exceptions.AthenaQueryError(
            "s3_output is not set",
        )

    def _get_workgroup_config(
        self,
    ) -> _WorkGroupConfig:
        enforced: bool
        wg_s3_output: Optional[str]
        wg_encryption: Optional[str]
        wg_kms_key: Optional[str]

        enforced, wg_s3_output, wg_encryption, wg_kms_key = False, None, None, None
        if self.workgroup is not None:
            res = self.get_work_group()
            enforced = res["WorkGroup"]["Configuration"]["EnforceWorkGroupConfiguration"]
            config: Dict[str, Any] = res["WorkGroup"]["Configuration"].get("ResultConfiguration")
            if config is not None:
                wg_s3_output = config.get("OutputLocation")
                encrypt_config: Optional[Dict[str, str]] = config.get("EncryptionConfiguration")
                wg_encryption = None if encrypt_config is None else encrypt_config.get("EncryptionOption")
                wg_kms_key = None if encrypt_config is None else encrypt_config.get("KmsKey")
        wg_config: _WorkGroupConfig = _WorkGroupConfig(
            enforced=enforced,
            s3_output=wg_s3_output,
            encryption=wg_encryption,
            kms_key=wg_kms_key,
        )
        _logger.debug("wg_config:\n%s", wg_config)
        return wg_config

    def get_work_group(self) -> Dict[str, Any]:

        return cast(
            Dict[str, Any],
            try_it(
                f=self.client_athena.get_work_group,
                ex=botocore.exceptions.ClientError,
                ex_code="ThrottlingException",
                max_num_tries=5,
                WorkGroup=self.workgroup,
            ),
        )

    def _get_query_metadata(  # noqa: C901
        self,
        query_execution_id: str,
        query_execution_payload: Optional[Dict[str, Any]] = None,
    ) -> _QueryMetadata:
        """Get query metadata."""
        if (query_execution_payload is not None) and (
            query_execution_payload["Status"]["State"] in _QUERY_FINAL_STATES
        ):
            if query_execution_payload["Status"]["State"] != "SUCCEEDED":
                reason: str = query_execution_payload["Status"]["StateChangeReason"]
                raise _exceptions.QueryFailed(f"Query error: {reason}")
            _query_execution_payload: Dict[str, Any] = query_execution_payload
        else:
            _query_execution_payload = self.wait_query(query_execution_id=query_execution_id)
        cols_types: Dict[str, str] = self.get_query_columns_types(query_execution_id=query_execution_id)
        _logger.debug("cols_types: %s", cols_types)
        dtype: Dict[str, str] = {}
        parse_timestamps: List[str] = []
        parse_dates: List[str] = []
        converters: Dict[str, Any] = {}
        binaries: List[str] = []
        col_name: str
        col_type: str
        for col_name, col_type in cols_types.items():
            if col_type == "array":
                raise _exceptions.UnsupportedType(
                    "List data type is not supported with regular (non-CTAS and non-UNLOAD) queries. "
                    "Please use ctas_approach=True or unload_approach=True for List columns."
                )
            if col_type == "row":
                raise _exceptions.UnsupportedType(
                    "Struct data type is not supported with regular (non-CTAS and non-UNLOAD) queries. "
                    "Please use ctas_approach=True or unload_approach=True for Struct columns."
                )
            pandas_type: str = athena2pandas(dtype=col_type)
            if (self.categories is not None) and (col_name in self.categories):
                dtype[col_name] = "category"
            elif pandas_type in ["datetime64", "date"]:
                parse_timestamps.append(col_name)
                if pandas_type == "date":
                    parse_dates.append(col_name)
            elif pandas_type == "bytes":
                dtype[col_name] = "string"
                binaries.append(col_name)
            elif pandas_type == "decimal":
                converters[col_name] = lambda x: Decimal(str(x)) if str(x) not in ("", "none", " ", "<NA>") else None
            else:
                dtype[col_name] = pandas_type

        output_location: Optional[str] = None
        if "ResultConfiguration" in _query_execution_payload:
            output_location = _query_execution_payload["ResultConfiguration"].get("OutputLocation")

        athena_statistics: Dict[str, Union[int, str]] = _query_execution_payload.get("Statistics", {})
        manifest_location: Optional[str] = str(athena_statistics.get("DataManifestLocation"))

        query_metadata: _QueryMetadata = _QueryMetadata(
            execution_id=query_execution_id,
            dtype=dtype,
            parse_timestamps=parse_timestamps,
            parse_dates=parse_dates,
            converters=converters,
            binaries=binaries,
            output_location=output_location,
            manifest_location=manifest_location,
            raw_payload=_query_execution_payload,
        )
        _logger.debug("query_metadata:\n%s", query_metadata)
        return query_metadata

    def get_query_columns_types(self, query_execution_id: str) -> Dict[str, str]:

        response: Dict[str, Any] = self.client_athena.get_query_results(
            QueryExecutionId=query_execution_id, MaxResults=1
        )
        col_info: List[Dict[str, str]] = response["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
        return dict(
            (c["Name"], f"{c['Type']}({c['Precision']},{c.get('Scale', 0)})")
            if c["Type"] in ["decimal"]
            else (c["Name"], c["Type"])
            for c in col_info
        )

    def _client(
        self,
        service_name: str,
        botocore_config: Optional[botocore.config.Config] = None,
        verify: Optional[Union[str, bool]] = None,
    ) -> boto3.client:
        """Create a valid boto3.client."""
        return self.session.client(
            service_name=service_name,
            use_ssl=True,
            verify=verify,
            config=default_botocore_config() if botocore_config is None else botocore_config,
        )

    def wait_query(self, query_execution_id: str) -> Dict[str, Any]:
        response: Dict[str, Any] = self.get_query_execution(query_execution_id=query_execution_id)
        state: str = response["Status"]["State"]
        while state not in _QUERY_FINAL_STATES:
            time.sleep(_QUERY_WAIT_POLLING_DELAY)
            response = self.get_query_execution(query_execution_id=query_execution_id)
            state = response["Status"]["State"]
        _logger.debug("state: %s", state)
        _logger.debug("StateChangeReason: %s", response["Status"].get("StateChangeReason"))
        if state == "FAILED":
            raise _exceptions.QueryFailed(response["Status"].get("StateChangeReason"))
        if state == "CANCELLED":
            raise _exceptions.QueryCancelled(response["Status"].get("StateChangeReason"))
        return response

    def get_query_execution(self, query_execution_id: str) -> Dict[str, Any]:
        response: Dict[str, Any] = try_it(
            f=self.client_athena.get_query_execution,
            ex=botocore.exceptions.ClientError,
            ex_code="ThrottlingException",
            max_num_tries=5,
            QueryExecutionId=query_execution_id,
        )
        return cast(Dict[str, Any], response["QueryExecution"])

    def _fetch_csv_result(
        self,
        query_metadata: _QueryMetadata,
    ) -> DataReturnType:
        _chunksize: Optional[int] = self.chunksize if isinstance(self.chunksize, int) else None
        _logger.debug("_chunksize: %s", _chunksize)
        if query_metadata.output_location is None or query_metadata.output_location.endswith(".csv") is False:
            chunked = _chunksize is not None
            return _empty_dataframe_response(chunked, query_metadata)
        path: str = query_metadata.output_location
        _logger.debug("Start CSV reading from %s", path)
        ret = self.s3_base.read_csv(
            path=[path],
            chunksize=self.chunksize,
            dtype=query_metadata.dtype,
            parse_dates=query_metadata.parse_timestamps,
            converters=query_metadata.converters,
            quoting=csv.QUOTE_ALL,
            keep_default_na=False,
            na_values=["", "NaN"],
            skip_blank_lines=False,
        )
        _logger.debug("Start type casting...")
        _logger.debug(type(ret))
        if _chunksize is None:
            df = _fix_csv_types(
                df=ret,
                parse_dates=query_metadata.parse_dates,
                binaries=query_metadata.binaries,
            )
            df = _apply_query_metadata(df=df, query_metadata=query_metadata)
            return df
        dfs = _fix_csv_types_generator(
            dfs=ret,
            parse_dates=query_metadata.parse_dates,
            binaries=query_metadata.binaries,
        )
        dfs = _add_query_metadata_generator(dfs=dfs, query_metadata=query_metadata)
        return dfs
