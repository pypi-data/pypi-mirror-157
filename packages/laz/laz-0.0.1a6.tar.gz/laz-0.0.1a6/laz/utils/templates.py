# std
from copy import deepcopy
from typing import Optional as Opt

# external
from jinja2 import Template

# internal
from laz.utils.errors import LazTypeError
from laz.utils.types import AtomicData, Data, DictData, ListData


def evaluate(data: Data, variables: Opt[DictData] = None) -> Data:
    if variables is None and isinstance(data, dict):
        variables = data
    data = deepcopy(data)
    return _expand(data, variables)


def _expand(data: Data, variables: DictData) -> Data:
    if isinstance(data, dict):
        return _expand_dict(data, variables)
    elif isinstance(data, list):
        return _expand_list(data, variables)
    elif isinstance(data, (type(None), bool, int, str)):
        return _expand_atomics(data, variables)
    else:
        raise LazTypeError(f'Cannot expand input of type {type(data)}')


def _expand_dict(data: DictData, variables: DictData) -> DictData:
    for key in data.keys():
        data[key] = _expand(data[key], variables)
    return data


def _expand_list(data: ListData, variables: DictData) -> ListData:
    for i in range(len(data)):
        data[i] = _expand(data[i], variables)
    return data


def _expand_atomics(data: AtomicData, variables: DictData) -> AtomicData:
    if isinstance(data, str):
        template = Template(data)
        rendered = template.render(**variables)
        return rendered
    else:
        return data
