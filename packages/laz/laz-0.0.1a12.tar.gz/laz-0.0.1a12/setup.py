# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['laz',
 'laz.cli',
 'laz.cli.subcommands',
 'laz.internal',
 'laz.model',
 'laz.plugins',
 'laz.utils']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3,<4', 'PyYAML>=6,<7', 'boto3[aws]']

entry_points = \
{'console_scripts': ['laz = laz.main:main']}

setup_kwargs = {
    'name': 'laz',
    'version': '0.0.1a12',
    'description': 'CLI tool to configure and run parameterized actions against targets.',
    'long_description': '# Laz\n\nA CLI tool to configure and run parameterized actions against targets.\n\n## Installation\n\nLaz currently requires Python 3.8+.\n\n```shell\npip3 install --user laz\n```\n\nYou can check your installation by running:\n\n```shell\nlaz version\n```\n\n## Documentation\n\n[https://joshwycuff.github.io/py-laz/](https://joshwycuff.github.io/py-laz/)\n',
    'author': 'Josh Wycuff',
    'author_email': 'Josh.Wycuff@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
