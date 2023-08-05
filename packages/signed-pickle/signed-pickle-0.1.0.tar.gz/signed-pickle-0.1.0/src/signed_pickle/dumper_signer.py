# -*- coding: utf-8 -*-
import hmac
import io
from contextlib import contextmanager
from os import PathLike
from typing import Optional, Protocol, Union

try:
    from lz4 import frame as def_comp

    COMPRESSION_KWARGS = {"compression_level": def_comp.COMPRESSIONLEVEL_MAX}
except ImportError:
    import zlib as def_comp  # type: ignore

    COMPRESSION_KWARGS = {"level": def_comp.Z_BEST_COMPRESSION}

DEFAULT_KEY = b"fe95e0f8-b3d2-478d-88b2-c74b6e7194a4"

FileType = Union[None, bytes, str, PathLike, io.IOBase]


class Compressor(Protocol):
    def compress(self, data: bytes, *args, **kwargs) -> bytes:
        ...

    def decompress(self, data: bytes, *args, **kwargs) -> bytes:
        ...


class DumperSigner:
    def __init__(
        self,
        key=None,
        hash_type="blake2b",
        hash_size: int = 64,
        compressor: Compressor = None,
        compressor_kwargs: dict = None,
    ):

        if key is None:
            self.key = DEFAULT_KEY
        else:
            self.key = key
        self.hash_type = hash_type
        self.hash_size = hash_size
        if compressor is None:
            self.compressor = def_comp
        if compressor_kwargs is None:
            self.compressor_kwargs = COMPRESSION_KWARGS

    def dump(
        self,
        obj: bytes,
        file: FileType = None,
    ) -> Optional[bytes]:
        _file: FileType
        if file is None:
            _file = io.BytesIO()
        else:
            _file = file
        with _maybe_open(_file, "wb") as fh:
            digest = hmac.new(self.key, obj, self.hash_type).digest()
            fh.write(digest)
            fh.write(self.compressor.compress(obj, **self.compressor_kwargs))
        if file is None:
            return _file.getvalue()  # type: ignore
        return None

    def load(self, file: Union[bytes, str, PathLike, io.IOBase]) -> bytes:
        if isinstance(file, bytes):
            file = io.BytesIO(file)
        with _maybe_open(file, "rb") as fh:
            digest = fh.read(self.hash_size)
            data = self.compressor.decompress(fh.read())
            expected_digest = hmac.new(self.key, data, self.hash_type).digest()
            if not hmac.compare_digest(digest, expected_digest):
                raise ValueError(
                    "data digest does not match expected digest, "
                    "did the file get corrupted or modified?"
                )
            return data


@contextmanager
def _maybe_open(file, *args, **kwargs):
    """
    Open the file if it's just a path, otherwise just yield
    :param file:
    :return:
    """
    if isinstance(file, io.IOBase):
        yield file
    else:
        with open(file, *args, **kwargs) as fh:
            yield fh
