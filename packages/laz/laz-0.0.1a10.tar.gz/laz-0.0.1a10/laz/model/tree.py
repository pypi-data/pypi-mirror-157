# std
from __future__ import annotations
from typing import List, Optional as Opt

# internal
from laz.model.configuration import Configuration
from laz.utils.funcs import flatten


class Node:
    configuration: Configuration
    parent: Opt[Node]
    children: List[Node]

    def __init__(
            self,
            configuration: Configuration,
            parent: Opt[Node] = None,
            children: Opt[List[Node]] = None,
    ):
        self.configuration = configuration
        self.parent = parent
        self.children = children or []

    @property
    def is_root(self):
        return self.parent is None

    @property
    def is_leaf(self):
        return len(self.children) == 0

    def add_child(self, node: Node):
        node.parent = self
        self.children.append(node)

    def add_children(self, nodes: List[Node]):
        for node in nodes:
            self.add_child(node)

    def nodes(self) -> List[Node]:
        if self.is_leaf:
            return [self]
        else:
            return [self] + flatten([n.nodes() for n in self.children])

    def root_path(self) -> List[Node]:
        if self.is_root:
            return [self]
        else:
            return self.parent.root_path() + [self]
