# std
import sys
from typing import Optional as Opt

# internal
from laz.utils import log


def main():
    log.debug(sys.argv[1:])
    subcommand = _subcommand()
    if len(sys.argv) > 1 and sys.argv[1] in ('help', '--help', '-h'):
        from laz.cli.subcommands.help import help
        help()
    elif len(sys.argv) == 2 and (sys.argv[1] == 'version' or sys.argv[1] == '--version'):
        from laz.cli.subcommands.version import version
        version()
    elif subcommand == 'init':
        from laz.cli.subcommands.init import init
        init()
    elif subcommand == 'tree':
        from laz.cli.subcommands.tree import tree
        tree()
    else:
        from laz.cli.root import root
        root()


def _subcommand() -> Opt[str]:
    for i, s in enumerate(sys.argv):
        if i > 0 and not s.startswith('-'):
            return sys.argv[i]


if __name__ == '__main__':
    sys.argv = [
        'laz',
        '-vvv',
        'pqr/dev',
        'echo',
        '{{ target.name }}',
    ]
    main()
