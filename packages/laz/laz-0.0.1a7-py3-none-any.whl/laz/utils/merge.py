# std
from copy import deepcopy
import itertools

# internal
from laz.utils.types import AtomicData, ListData, DictData, Data
from laz.utils.errors import LazTypeError


def merge(left: Data, right: Data) -> Data:
    if type(left) != type(right):
        raise LazTypeError(f'merge inputs must be same type. Got {type(left)} and {type(right)}')
    return _merge(deepcopy(left), deepcopy(right))


def _merge(left: Data, right: Data) -> Data:
    if isinstance(left, dict) and isinstance(right, dict):
        return _merge_dicts(left, right)
    elif isinstance(left, list) and isinstance(right, list):
        return _merge_lists(left, right)
    elif isinstance(left, (type(None), bool, int, str)) and isinstance(right, (type(None), bool, int, str)):
        return _merge_atomics(left, right)
    elif left is None:
        return right
    elif right is None:
        return left
    else:
        raise LazTypeError(f'merge inputs must be same type. Got {type(left)} and {type(right)}')


def _merge_dicts(left: DictData, right: DictData) -> DictData:
    for key in right.keys():
        l = left.get(key)
        r = right.get(key)
        left[key] = _merge(l, r)
    return left


def _merge_lists(left: ListData, right: ListData) -> ListData:
    new_list = [None] * max(len(left), len(right))
    for i, (l, r) in enumerate(itertools.zip_longest(left, right)):
        new_list[i] = _merge(l, r)
    return new_list


def _merge_atomics(left: AtomicData, right: AtomicData) -> AtomicData:
    if left is None and right is not None:
        return right
    elif left is not None and right is None:
        return left
    return right
