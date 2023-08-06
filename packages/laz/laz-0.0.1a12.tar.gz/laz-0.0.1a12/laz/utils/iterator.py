# std
from __future__ import annotations
from typing import (
    Generic,
    Iterable,
    Iterator as _Iterator,
    Optional as Opt,
    Sized,
    TypeVar,
    Union,
)

# types
T = TypeVar('T')


class Iterator(Generic[T]):

    def __init__(self, iterable: Union[Iterable[T], Sized]):
        self._iterator: _Iterator[T] = iter(iterable)
        self._index: int = -1
        self._length: int = len(iterable)
        self._value: Opt[T] = None

    def __iter__(self):
        return self

    def __next__(self) -> Iterator:
        self._index += 1
        self._value = next(self._iterator)
        return self

    @property
    def is_first(self) -> bool:
        return self._index == 0

    @property
    def is_last(self) -> bool:
        return self._index == self._length - 1

    @property
    def value(self) -> T:
        return self._value
