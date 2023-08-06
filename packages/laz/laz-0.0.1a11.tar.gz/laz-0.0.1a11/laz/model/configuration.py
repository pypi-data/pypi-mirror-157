# std
from __future__ import annotations
import os
from typing import List

# external
import yaml
from yaml.loader import SafeLoader

# internal
from laz.model.base import BaseObject
from laz.model.target import Target


class Configuration(BaseObject):

    @property
    def filepath(self):
        return self.id

    @property
    def name(self):
        return os.path.basename(os.path.dirname(self.filepath))

    @property
    def target_names(self) -> List[str]:
        return list(self.data.get('targets', {}).keys())

    def get_target(self, name: str) -> Target:
        return Target(name, **self.data.get('targets', {}).get(name, {}) or {})

    @classmethod
    def deserialize(cls, id: str, serialized: str) -> Configuration:
        data = yaml.load(serialized, Loader=SafeLoader) or {}
        if 'env' in data:
            if data['env'] is None:
                data['env'] = {}
            assert isinstance(data['env'], dict)
            data['env'] = {k: str(v) for k, v in data['env'].items()}
        return cls(id, **data)

    @classmethod
    def load(cls, filepath: str) -> Configuration:
        with open(filepath, 'r') as fh:
            return Configuration.deserialize(filepath, fh.read())
