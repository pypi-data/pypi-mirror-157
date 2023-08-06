# std
from contextlib import contextmanager
import os


@contextmanager
def in_dir(dirpath: str):
    previous_dirpath = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(previous_dirpath)
