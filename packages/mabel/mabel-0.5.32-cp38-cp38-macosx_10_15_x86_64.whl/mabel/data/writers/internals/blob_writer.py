import threading
import orjson
import json
import zstandard
from ...internals.index import IndexBuilder
from ...internals.records import flatten
from ....logging import get_logger
from ....utils.paths import get_parts
from ....utils import safe_field_name
from ....errors import MissingDependencyError


BLOB_SIZE = 64 * 1024 * 1024  # 64Mb, 16 files per gigabyte
SUPPORTED_FORMATS_ALGORITHMS = ("jsonl", "zstd", "parquet", "text", "flat")


class BlobWriter(object):

    # in som failure scenarios commit is called before __init__, so we need to define
    # this variable outside the __init__.
    buffer = bytearray()

    def __init__(
        self,
        *,  # force params to be named
        inner_writer=None,  # type:ignore
        blob_size: int = BLOB_SIZE,
        format: str = "zstd",
        **kwargs,
    ):

        self.format = format
        self.maximum_blob_size = blob_size

        if format not in SUPPORTED_FORMATS_ALGORITHMS:
            raise ValueError(
                f"Invalid format `{format}`, valid options are {SUPPORTED_FORMATS_ALGORITHMS}"
            )

        kwargs["format"] = format
        self.inner_writer = inner_writer(**kwargs)  # type:ignore

        self.open_buffer()

    def append(self, record: dict = {}):
        # serialize the record
        if self.format == "text":
            if isinstance(record, bytes):
                serialized = record + b"\n"
            elif isinstance(record, str):
                serialized = record.encode() + b"\n"
            else:
                serialized = str(record).encode() + b"\n"
        elif self.format == "flat":
            serialized = orjson.dumps(flatten(record)) + b"\n"  # type:ignore
        elif hasattr(record, "mini"):
            serialized = record.mini + b"\n"  # type:ignore
        else:
            try:
                serialized = orjson.dumps(record) + b"\n"  # type:ignore
            except TypeError:
                serialized = json.dumps(record).encode() + b"\n"

        # the newline isn't counted so add 1 to get the actual length
        # if this write would exceed the blob size, close it so another
        # blob will be created
        if len(self.buffer) > self.maximum_blob_size and self.records_in_buffer > 0:
            self.commit()
            self.open_buffer()

        # write the record to the file
        self.buffer.extend(serialized)
        self.records_in_buffer += 1

        return self.records_in_buffer

    def commit(self):

        committed_blob_name = ""

        if len(self.buffer) > 0:

            lock = threading.Lock()

            try:
                lock.acquire(blocking=True, timeout=10)

                if self.format == "parquet":
                    try:
                        import pyarrow.json
                        import pyarrow.parquet as pq  # type:ignore
                    except ImportError as err:  # pragma: no cover
                        raise MissingDependencyError(
                            "`pyarrow` is missing, please install or includein requirements.txt"
                        )

                    import io
                    from functools import reduce

                    tempfile = io.BytesIO()

                    # convert to a list of dicts
                    temp_list = [
                        orjson.loads(record) for record in self.buffer.splitlines()
                    ]

                    # When writing to Parquet, the table gets the schema from the first
                    # row, if this row is missing columns (shouldn't, but it happens)
                    # it will be missing for all records, so get the columns from the
                    # entire dataset and ensure all records have the same columns.

                    # first, we get all the columns, from all the records
                    columns = reduce(
                        lambda x, y: x + [a for a in y.keys() if a not in x],
                        temp_list,
                        [],
                    )

                    # then we make sure each row has all the columns
                    temp_list = [
                        {column: row.get(column) for column in columns}
                        for row in temp_list
                    ]

                    pytable = pyarrow.Table.from_pylist(temp_list)
                    pyarrow.parquet.write_table(
                        pytable, where=tempfile, compression="zstd"
                    )

                    tempfile.seek(0)
                    self.buffer = tempfile.read()

                if self.format == "zstd":
                    # zstandard is an non-optional installed dependency
                    self.buffer = zstandard.compress(self.buffer)

                committed_blob_name = self.inner_writer.commit(
                    byte_data=bytes(self.buffer), override_blob_name=None
                )

                if "BACKOUT" in committed_blob_name:
                    get_logger().warning(
                        f"{self.records_in_buffer:n} failed records written to BACKOUT partition `{committed_blob_name}`"
                    )
                get_logger().debug(
                    {
                        "committed_blob": committed_blob_name,
                        "records": self.records_in_buffer,
                        "bytes": len(self.buffer),
                    }
                )
            finally:
                lock.release()

        self.buffer = bytearray()
        return committed_blob_name

    def open_buffer(self):
        self.buffer = bytearray()
        self.records_in_buffer = 0

    def __del__(self):
        # this should never be relied on to save data
        self.commit()
