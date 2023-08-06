# std
from __future__ import annotations
import json
import yaml
from yaml.loader import SafeLoader

# internal
from laz.utils.types import Data
from laz.model.serializable import Serializable
from laz.model.stackable import Stackable


class BaseObject(Serializable, Stackable):

    def __init__(self, id: str, **data: Data):
        self.id = id
        self.data = data

    def json(self) -> str:
        return json.dumps(self.data, indent=2, default=str)

    def serialize(self) -> str:
        return yaml.dump(self.data)

    @classmethod
    def deserialize(cls, id: str, serialized: str) -> BaseObject:
        data = yaml.load(serialized, Loader=SafeLoader) or {}
        return cls(id, **data)
