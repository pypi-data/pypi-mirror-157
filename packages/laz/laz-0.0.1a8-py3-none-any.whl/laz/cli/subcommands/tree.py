# std
from typing import List
# internal
from laz.utils.logging import get_logger
from laz.cli.parser import parser
from laz.utils.load import load
from laz.model.tree import Node
from laz.utils.iterator import Iterator
from laz.utils.node import get_node_configuration
from laz.model.resolver import Resolver


subparsers = parser.add_subparsers(required=True)

parser_tree = subparsers.add_parser('tree')
parser_tree.add_argument('--show-targets', '-t', action='store_true', default=False, help='Show targets.')
parser_tree.add_argument('--show-paths', '-p', action='store_true', default=False, help='Show paths.')

# config
SHOW_TARGETS = False
SHOW_PATHS = False


def tree():
    global SHOW_TARGETS, SHOW_PATHS
    args = parser.parse_args()
    get_logger(verbosity=args.verbose)
    SHOW_TARGETS = args.show_targets
    SHOW_PATHS = args.show_paths
    root = load()
    print(root.configuration.name)
    if args.show_targets:
        _targets(root, '', len(root.children) == 0)
    for child in Iterator(root.children):
        _tree(child.value, '', child.is_last)


def _tree(
        node: Node,
        prefix: str = '',
        last: bool = False,
):
    symbol = '└─' if last else '├─'
    path = f'({Resolver.get_name_path(node)})' if SHOW_PATHS else ''
    print(f'{prefix}{symbol} {node.configuration.name}/ {path}')

    if SHOW_TARGETS:
        _targets(node, prefix, last)

    for child in Iterator(node.children):
        _tree(child.value, prefix + '│  ', child.is_last)


def _targets(node: Node, prefix: str, last: bool):
    prefix = prefix + '   ' if last else prefix + '│  '
    for target_name in Iterator(_get_target_names(node)):
        symbol = '└─' if target_name.is_last and len(node.children) == 0 else '├─'
        print(f'{prefix}{symbol} {target_name.value}')


def _get_target_names(node: Node) -> List[str]:
    configuration = get_node_configuration(node)
    return configuration.target_names
