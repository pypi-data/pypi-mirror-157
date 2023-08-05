# -*- coding: utf-8 -*-
from __future__ import annotations

import base64
import dataclasses
import hmac
import importlib
import io
from contextlib import contextmanager
from os import PathLike
from types import ModuleType
from typing import Any, Callable, Optional, Protocol, Type, Union

try:
    from lz4 import frame as def_comp

    COMPRESSOR_KWARGS = {"compression_level": def_comp.COMPRESSIONLEVEL_MAX}
except ImportError:
    import zlib as def_comp  # type: ignore

    COMPRESSOR_KWARGS = {"level": def_comp.Z_BEST_COMPRESSION}

DEFAULT_KEY = b"fe95e0f8-b3d2-478d-88b2-c74b6e7194a4"

FileType = Union[bytes, str, PathLike, io.IOBase]
HashType = Union[str, Callable, ModuleType]


class Compressor(Protocol):
    def compress(self, data: bytes, *args, **kwargs) -> bytes:
        ...

    def decompress(self, data: bytes, *args, **kwargs) -> bytes:
        ...


@dataclasses.dataclass
class SignerOptions:
    dumper_class: Type[DumperSigner]
    key: bytes = DEFAULT_KEY
    hash_type: HashType = "blake2b"
    hash_size: int = 64
    compressor: Compressor = def_comp
    compressor_kwargs: dict = dataclasses.field(default_factory=lambda: COMPRESSOR_KWARGS)

    magic_bytes = b"\xd5\xd5"
    header_format = {
        # section, length
        "magic_bytes": (2, "raw"),
        "hash_size": (2, "int"),
        "dumper_class": (16, "class"),
        "hash_type": (12, "str"),
        "compressor": (16, "class"),
    }

    @classmethod
    @property
    def header_size(cls) -> int:
        return sum(a[0] for a in cls.header_format.values())

    def header(self) -> bytes:
        header = b""
        for k, (length, t) in self.header_format.items():
            if t == "raw":
                header += getattr(self, k)
            elif t == "int":
                header += int(getattr(self, k)).to_bytes(length, "little")
            elif t == "class":
                header += getattr(self, k).__name__.ljust(length).encode("utf8")
            elif t == "str":
                header += getattr(self, k).ljust(length).encode("utf8")
        return header

    @classmethod
    def decode_header(cls, header: bytes, key=None, compressor_kwargs=None):
        if header[:2] != cls.magic_bytes or len(header) != cls.header_size:
            raise ValueError("Invalid header")
        _new: SignerOptions = cls.__new__(cls)
        for k, (length, t) in cls.header_format.items():
            v: Any = header[:length]
            if t == "raw":
                setattr(_new, k, v)
            elif t == "int":
                setattr(_new, k, int.from_bytes(v, "little"))
            elif t == "class":
                v = v.decode("utf8").strip()
                if v in DumperSigner.subclasses():
                    setattr(_new, k, DumperSigner.subclasses()[v])
                else:
                    setattr(_new, k, importlib.import_module(v))
            elif t == "str":
                setattr(_new, k, v.decode("utf8").strip())
            header = header[length:]
        if key is None:
            _new.key = DEFAULT_KEY
        else:
            _new.key = key
        if compressor_kwargs is None:
            _new.compressor_kwargs = COMPRESSOR_KWARGS
        else:
            _new.compressor_kwargs = compressor_kwargs
        return _new


class DumperSigner:
    @classmethod
    def subclasses(cls):
        main_ancestor = cls.mro()[-2]
        return {a.__name__: a for a in main_ancestor.__subclasses__() + [main_ancestor]}

    def __init__(
        self,
        key: Optional[bytes] = None,
        hash_type="blake2b",
        hash_size: int = 64,
        compressor: Compressor = None,
        compressor_kwargs: dict = None,
        use_header=True,
        options: Optional[SignerOptions] = None,
    ):
        self.use_header = use_header
        if key is None:
            key = DEFAULT_KEY
        if compressor is None:
            compressor = def_comp
        if compressor_kwargs is None:
            compressor_kwargs = COMPRESSOR_KWARGS
        if options is None:
            options = SignerOptions(
                dumper_class=self.__class__,
                key=key,
                hash_type=hash_type,
                hash_size=hash_size,
                compressor=compressor,
                compressor_kwargs=compressor_kwargs,
            )
        self.options = options

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
            digest = hmac.new(self.options.key, obj, self.options.hash_type).digest()
            if self.use_header:
                fh.write(self.options.header())
            fh.write(digest)
            fh.write(self.options.compressor.compress(obj, **self.options.compressor_kwargs))
        if file is None:
            return _file.getvalue()  # type: ignore
        return None

    @classmethod
    def load(
        cls, file: FileType, key=None, compressor_kwargs=None
    ) -> tuple[bytes, Type[DumperSigner]]:
        if isinstance(file, bytes):
            file = io.BytesIO(file)
        with _maybe_open(file, "rb") as fh:
            buf = fh.read(len(SignerOptions.magic_bytes))
            cls_kwargs = {}
            if buf != SignerOptions.magic_bytes:
                # no header, assume defaults

                this_cls = cls
                cls_kwargs = {"key": key, "compressor_kwargs": compressor_kwargs}
            else:
                # header found, decode it
                buf += fh.read(SignerOptions.header_size - len(buf))  # type: ignore
                options = SignerOptions.decode_header(
                    buf, key=key, compressor_kwargs=compressor_kwargs
                )
                buf = b""
                this_cls = options.dumper_class
                cls_kwargs = {"options": options}
            _new = this_cls(**cls_kwargs)
            digest = buf + fh.read(_new.options.hash_size - len(buf))
            data = fh.read()
            data = _new._load(digest, data)
            return data, _new.options.dumper_class

    def _load(self, digest, compressed_data):

        data = self.options.compressor.decompress(compressed_data)
        expected_digest = hmac.new(self.options.key, data, self.options.hash_type).digest()
        if not hmac.compare_digest(digest, expected_digest):
            raise ValueError(
                "data digest does not match expected digest, "
                "did the file get corrupted or modified?"
            )
        return data

    def to_base64(self, obj: bytes) -> bytes:
        return base64.b64encode(self.dump(obj))  # type: ignore

    @classmethod
    def from_base64(cls, b64: bytes) -> Any:
        return cls.load(base64.b64decode(b64.strip()))[0]

    def to_base85(self, obj: bytes) -> bytes:
        return base64.b85encode(self.dump(obj))  # type: ignore

    @classmethod
    def from_base85(cls, b85: bytes) -> Any:
        return cls.load(base64.b85decode(b85.strip()))[0]


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
