# std
from __future__ import annotations


class Serializable:

    def serialize(self) -> str:
        raise NotImplementedError

    @classmethod
    def deserialize(cls, name: str, serialized: str) -> Serializable:
        raise NotImplementedError
