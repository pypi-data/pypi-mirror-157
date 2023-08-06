# std
import argparse
import traceback
from typing import List

# internal
from laz.utils.errors import LazRuntimeError
from laz.model.tree import Node
from laz.model.path import Path
from laz.model.resolver import Resolver
from laz.model.target import Target
from laz.model.act import Act


class Runner:

    def __init__(self, root_node: Node, cli_args: argparse.Namespace, args: List[str]):
        self.root_node = root_node
        self.cli_args = cli_args
        self.path = Path(args[0])
        self.args = args[1:]
        self.root_node.configuration.push({
            'path': args[0],
            'args': args[1:],
        })

    def resolve(self) -> List[Target]:
        resolver = Resolver(self.root_node, self.path)
        targets = resolver.resolve()
        if self.cli_args.reverse:
            targets.reverse()
        return targets

    def run(self):
        failures = []
        targets = self.resolve()
        for target in targets:
            try:
                act = Act.new(target, args=' '.join(self.args))
                act.act()
            except Exception as e:
                failures.append((e, traceback.format_exc()))
        for failure in failures:
            print(failure)
        if failures:
            raise LazRuntimeError('Some actions failed')
