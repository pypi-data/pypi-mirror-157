# std
from typing import Dict, List, Union

AtomicData = Union[type(None), bool, int, str]
ListData = List[Union[AtomicData, 'ListData', 'DictData']]
DictData = Dict[str, Union[AtomicData, ListData, 'DictData']]
Data = Union[AtomicData, ListData, DictData]
