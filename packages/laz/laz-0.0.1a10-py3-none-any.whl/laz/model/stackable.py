# std
from __future__ import annotations
from typing import List

# internal
from laz.utils.types import DictData
from laz.utils.merge import merge


class Stackable:

    _stack: List[DictData] = None
    data: DictData = None

    def push(self, data: DictData):
        if self._stack is None:
            self._stack = []
        self._stack.append(self.data)
        self.data = merge(self.data, data)

    def pop(self):
        self.data = self._stack.pop()

    def replace(self, data: DictData):
        self._stack[-1] = data
        self.data = data
