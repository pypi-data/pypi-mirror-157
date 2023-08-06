# std
import os
import yaml

# internal
from laz.utils.logging import get_logger
from laz.utils import log
from laz.cli.parser import parser


subparsers = parser.add_subparsers(required=True)

parser_init = subparsers.add_parser('init')

def init():
    args = parser.parse_args()
    get_logger(verbosity=args.verbose)

    if os.path.isfile('laz.yml'):
        log.error('laz.yml exists')
        exit(1)

    data = yaml.safe_dump({
        'env': {
            'example': 'value',
        },
        'targets': {
            'dev': None,
        },
        'actions': {
            'example': 'echo $example',
            'hello': 'echo {{ target.name }}',
        },
    }, sort_keys=False).replace('null', '')

    with open('laz.yml', 'w') as fh:
        fh.write(data)
