# std
from contextlib import contextmanager
from copy import deepcopy
import os
from typing import Dict

# internal
from laz.utils.merge import merge


@contextmanager
def in_dir(dirpath: str):
    previous_dirpath = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(previous_dirpath)


@contextmanager
def with_environ(env: Dict[str, str]):
    original = deepcopy(os.environ)
    try:
        os.environ = merge(dict(os.environ), env)
        yield
    finally:
        os.environ = original
