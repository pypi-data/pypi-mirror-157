# -*- coding: utf-8 -*-
import io
import pickle  # nosec
from os import PathLike
from typing import Any, Optional, Union

from .dumper_signer import DumperSigner


class PickleSigner(DumperSigner):
    def _load(self, digest, compressed_data):
        # noinspection PickleLoad
        return pickle.loads(super()._load(digest, compressed_data))  # nosec

    def dump(
        self,
        obj: Any,
        file: Union[None, bytes, str, PathLike, io.IOBase] = None,
    ) -> Optional[bytes]:
        return super().dump(pickle.dumps(obj, protocol=5), file)
