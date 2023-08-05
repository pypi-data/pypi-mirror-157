# -*- coding: utf-8 -*-
from __future__ import annotations

import io
import logging
import math
import socket
from contextlib import contextmanager
from errno import ESPIPE
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
    cast,
)

from botocore.exceptions import ReadTimeoutError

from . import _exceptions
from .utils import parse_path, try_it

if TYPE_CHECKING:
    from .s3_base import S3Base

_logger: logging.Logger = logging.getLogger(__name__)

_S3_RETRYABLE_ERRORS: Tuple[Any, Any, Any] = (socket.timeout, ConnectionError, ReadTimeoutError)

_MIN_WRITE_BLOCK: int = 5_242_880  # 5 MB (5 * 2**20)


class S3ObjectBase(io.RawIOBase):  # pylint: disable=too-many-instance-attributes
    """Class to abstract S3 objects as ordinary files."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        path: str,
        s3_block_size: int,
        mode: str,
        # s3_additional_kwargs: Optional[Dict[str, str]],
        s3_base: S3Base,
        newline: Optional[str],
        encoding: Optional[str],
        # version_id: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._s3_base = s3_base
        self._boto3_session = self._s3_base.session
        self._client = self._s3_base.client_s3
        self._newline: str = "\n" if newline is None else newline
        self._encoding: str = "utf-8" if encoding is None else encoding
        self._bucket, self._key = parse_path(path=path)
        # self._version_id = version_id
        # self._boto3_session: boto3.Session = boto3_session
        if mode not in {"rb", "wb", "r", "w"}:
            raise NotImplementedError(f"File mode must be {'rb', 'wb', 'r', 'w'}, not {mode}")
        self._mode: str = "rb" if mode is None else mode
        self._one_shot_download: bool = False
        if 0 < s3_block_size < 3:
            raise _exceptions.InvalidArgumentValue(
                "s3_block_size MUST > 2 to define a valid size or "
                "< 1 to avoid blocks and always execute one shot downloads."
            )
        if s3_block_size <= 0:
            _logger.debug("s3_block_size of %d, enabling one_shot_download.", s3_block_size)
            self._one_shot_download = True
        self._s3_block_size: int = s3_block_size
        self._s3_half_block_size: int = s3_block_size // 2
        # self._s3_additional_kwargs: Dict[str, str] = {} if s3_additional_kwargs is None else s3_additional_kwargs

        # self._client: boto3.client = _client(service_name="s3", session=self._boto3_session)
        self._loc: int = 0

        if self.readable() is True:
            self._cache: bytes = b""
            self._start: int = 0
            self._end: int = 0
            size: Optional[int] = self._s3_base.size_objects(
                path=[path],
                # version_id=version_id,
                # s3_additional_kwargs=self._s3_additional_kwargs,
            )[path]
            if size is None:
                raise _exceptions.InvalidArgumentValue(f"S3 object w/o defined size: {path}")
            self._size: int = size
            _logger.debug("self._size: %s", self._size)
            _logger.debug("self._s3_block_size: %s", self._s3_block_size)

        else:
            raise RuntimeError(f"Invalid mode: {self._mode}")

    @classmethod
    @contextmanager
    def open_s3_object(
        cls,
        s3_base: S3Base,
        path: str,
        mode: str,
        # version_id: Optional[str] = None,
        # s3_additional_kwargs: Optional[Dict[str, str]] = None,
        s3_block_size: int = -1,  # One shot download
        newline: Optional[str] = "\n",
        encoding: Optional[str] = "utf-8",
    ) -> Iterator[Union["S3ObjectBase", io.TextIOWrapper]]:
        """Return a _S3Object or TextIOWrapper based in the received mode."""
        s3obj: Optional[S3ObjectBase] = None
        text_s3obj: Optional[io.TextIOWrapper] = None
        try:
            s3obj = cls(
                path=path,
                s3_block_size=s3_block_size,
                mode=mode,
                # version_id=version_id,
                s3_base=s3_base,
                # s3_additional_kwargs=s3_additional_kwargs,
                encoding=encoding,
                newline=newline,
            )
            if "b" in mode:  # binary
                yield s3obj
            else:  # text
                text_s3obj = io.TextIOWrapper(
                    buffer=cast(BinaryIO, s3obj),
                    encoding=encoding,
                    newline=newline,
                    line_buffering=False,
                    write_through=False,
                )
                yield text_s3obj
        finally:
            if text_s3obj is not None and text_s3obj.closed is False:
                text_s3obj.close()
            if s3obj is not None and s3obj.closed is False:
                s3obj.close()

    def __enter__(self) -> Union["S3ObjectBase"]:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        """Close the context."""
        _logger.debug("exc_type: %s", exc_type)
        _logger.debug("exc_value: %s", exc_value)
        _logger.debug("exc_traceback: %s", exc_traceback)
        self.close()

    def __del__(self) -> None:
        """Delete object tear down."""
        self.close()

    def __next__(self) -> bytes:
        """Next line."""
        out: Union[bytes, None] = self.readline()
        if not out:
            raise StopIteration
        return out

    next = __next__

    def __iter__(self) -> "S3ObjectBase":
        """Iterate over lines."""
        return self

    @staticmethod
    def _merge_range(ranges: List[Tuple[int, bytes]]) -> bytes:
        return b"".join(data for start, data in sorted(ranges, key=lambda r: r[0]))

    def _fetch_range_proxy(self, start: int, end: int) -> bytes:
        _logger.debug("Fetching: s3://%s/%s - Range: %s-%s", self._bucket, self._key, start, end)

        # boto3_kwargs: Dict[str, Any] = get_botocore_valid_kwargs(
        #     function_name="get_object",
        #     # s3_additional_kwargs=self._s3_additional_kwargs
        # )

        return self._fetch_range(
            range_values=(start, end),
            bucket=self._bucket,
            key=self._key,
            # boto3_kwargs=boto3_kwargs,
            # version_id=self._version_id,
        )[1]

    def _fetch(self, start: int, end: int) -> None:  # noqa: C901
        if end > self._size:
            raise ValueError(f"Trying to fetch byte (at position {end - 1}) beyond file size ({self._size})")
        if start < 0:
            raise ValueError(f"Trying to fetch byte (at position {start}) beyond file range ({self._size})")

        if start >= self._start and end <= self._end:
            return None  # Does not require download

        if self._one_shot_download:
            self._start = 0
            self._end = self._size
            self._cache = self._fetch_range_proxy(self._start, self._end)
            return None

        if end - start >= self._s3_block_size:  # Fetching length greater than cache length
            self._cache = self._fetch_range_proxy(start, end)
            self._start = start
            self._end = end
            return None

        # Calculating block START and END positions
        _logger.debug("Downloading: %s (start) / %s (end)", start, end)
        mid: int = int(math.ceil((start + (end - 1)) / 2))
        new_block_start: int = mid - self._s3_half_block_size
        new_block_start = new_block_start + 1 if self._s3_block_size % 2 == 0 else new_block_start
        new_block_end: int = mid + self._s3_half_block_size + 1
        _logger.debug("new_block_start: %s / new_block_end: %s / mid: %s", new_block_start, new_block_end, mid)
        if new_block_start < 0 and new_block_end > self._size:  # both ends overflowing
            new_block_start = 0
            new_block_end = self._size
        elif new_block_end > self._size:  # right overflow
            new_block_start = new_block_start - (new_block_end - self._size)
            new_block_start = 0 if new_block_start < 0 else new_block_start
            new_block_end = self._size
        elif new_block_start < 0:  # left overflow
            new_block_end = new_block_end - new_block_start
            new_block_end = self._size if new_block_end > self._size else new_block_end
            new_block_start = 0
        _logger.debug(
            "new_block_start: %s / new_block_end: %s/ self._start: %s / self._end: %s",
            new_block_start,
            new_block_end,
            self._start,
            self._end,
        )

        # Calculating missing bytes in cache
        if (  # Full block download
            (new_block_start < self._start and new_block_end > self._end)
            or new_block_start > self._end
            or new_block_end < self._start
        ):
            self._cache = self._fetch_range_proxy(new_block_start, new_block_end)
        elif new_block_end > self._end:
            prune_diff: int = new_block_start - self._start
            self._cache = self._cache[prune_diff:] + self._fetch_range_proxy(self._end, new_block_end)
        elif new_block_start < self._start:
            prune_diff = new_block_end - self._end
            self._cache = self._fetch_range_proxy(new_block_start, self._start) + self._cache[:prune_diff]
        else:
            raise RuntimeError("Wrangler's cache calculation error.")
        self._start = new_block_start
        self._end = new_block_end

        return None

    def tell(self) -> int:
        """Return the current file location."""
        return self._loc

    def seek(self, loc: int, whence: int = 0) -> int:
        """Set current file location."""
        if self.readable() is False:
            raise OSError(ESPIPE, "Seek only available in read mode")
        if whence == 0:
            loc_tmp: int = loc
        elif whence == 1:
            loc_tmp = self._loc + loc
        elif whence == 2:
            loc_tmp = self._size + loc
        else:
            raise ValueError(f"invalid whence ({whence}, should be 0, 1 or 2).")
        if loc_tmp < 0:
            raise ValueError("Seek before start of file")
        self._loc = loc_tmp
        return self._loc

    def readable(self) -> bool:
        """Return whether this object is opened for reading."""
        return "r" in self._mode

    def seekable(self) -> bool:
        """Return whether this object is opened for seeking."""
        return self.readable()

    def writable(self) -> bool:
        return False

    def close(self) -> None:
        """Clean up the cache."""
        if self.closed:  # pylint: disable=using-constant-test
            return None
        if self.readable():
            self._cache = b""
        else:
            raise RuntimeError(f"Invalid mode: {self._mode}")
        super().close()
        return None

    def read(self, length: int = -1) -> bytes:
        """Return cached data and fetch on demand chunks."""
        if self.readable() is False:
            raise ValueError("File not in read mode.")
        if self.closed is True:
            raise ValueError("I/O operation on closed file.")
        if length < 0 or self._loc + length > self._size:
            length = self._size - self._loc

        self._fetch(self._loc, self._loc + length)
        out: bytes = self._cache[self._loc - self._start : self._loc - self._start + length]
        self._loc += len(out)
        return out

    def readline(self, length: Optional[int] = -1) -> bytes:
        """Read until the next line terminator."""
        length = -1 if length is None else length
        end: int = self._loc + self._s3_block_size
        end = self._size if end > self._size else end
        self._fetch(self._loc, end)
        while True:
            found: int = self._cache[self._loc - self._start :].find(self._newline.encode(encoding=self._encoding))

            if 0 < length < found:
                return self.read(length + 1)
            if found >= 0:
                return self.read(found + 1)
            if self._end >= self._size:
                return self.read(-1)

            end = self._end + self._s3_half_block_size
            end = self._size if end > self._size else end
            self._fetch(self._loc, end)

    def _fetch_range(
        self,
        range_values: Tuple[int, int],
        bucket: str,
        key: str,
        # boto3_kwargs: Dict[str, Any],
        version_id: Optional[str] = None,
    ) -> Tuple[int, bytes]:
        start, end = range_values
        _logger.debug(
            "Fetching: s3://%s/%s - VersionId: %s - Range: %s-%s",
            bucket,
            key,
            version_id,
            start,
            end,
        )
        resp: Dict[str, Any]
        # if version_id:
        #     boto3_kwargs["VersionId"] = version_id
        resp = try_it(
            f=self._client.get_object,
            ex=_S3_RETRYABLE_ERRORS,
            base=0.5,
            max_num_tries=6,
            Bucket=bucket,
            Key=key,
            Range=f"bytes={start}-{end - 1}",
            # **boto3_kwargs,
        )
        return start, cast(bytes, resp["Body"].read())
