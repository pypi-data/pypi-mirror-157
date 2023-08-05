import decimal
from typing import overload, Any, Union, Optional, Generic, TypeVar, Type, Tuple, Iterable
from datetime import datetime, time, date
from uuid import UUID

from yarl import URL

from . import DDDStructure
from .core import Nothing

_T = TypeVar('_T')


class Field(Generic[_T]):
    @overload
    def __init__(self, *, default: _T = Nothing, nullable: bool = False, description=''):
        ...

    @overload
    def __get__(self, instance, owner) -> _T:
        ...


class String(Field[str]):

    def __get__(self, instance, owner) -> str:
        ...

    ...


class Uuid(Field[UUID]):
    @overload
    def __get__(self, instance, owner) -> UUID:
        ...


class Integer(Field[int]):
    @overload
    def __get__(self, instance, owner) -> int:
        ...


class Float(Field[float]):
    @overload
    def __get__(self, instance, owner) -> float:
        ...


class Decimal(Field[decimal.Decimal]):
    @overload
    def __init__(self, places: Union[int, None] = None,
                 rounding: Union[str, None] = None,
                 *, default: Any = Nothing, nullable: bool = False):
        ...

    @overload
    def __get__(self, instance, owner) -> decimal.Decimal:
        ...


class Boolean(Field[bool]):
    @overload
    def __init__(self, *, truthy: Optional[Iterable] = None, falsy: Optional[Iterable] = None,
                 default: Any = Nothing, nullable: bool = False):
        ...

    @overload
    def __get__(self, instance, owner) -> bool:
        ...


class Datetime(Field[datetime]):
    @overload
    def __get__(self, instance, owner) -> datetime:
        ...


class Time(Field[time]):
    @overload
    def __get__(self, instance, owner) -> time:
        ...


class Date(Field[date]):
    @overload
    def __get__(self, instance, owner) -> date:
        ...


class Url(Field[URL]):
    @overload
    def __get__(self, instance, owner) -> URL:
        ...


class Email(Field[str]):
    @overload
    def __get__(self, instance, owner) -> str:
        ...


class List(Field):
    @overload
    def __init__(self, instance: Field, *, allow_empty=False,
                 nullable: bool = False):
        ...

    @overload
    def __get__(self, instance, owner) -> Tuple[...]:
        ...


class Structure(Field):
    @overload
    def __init__(self, structure: Type[DDDStructure], *, nullable: bool = False):
        ...

    @overload
    def __get__(self, instance, owner) -> DDDStructure:
        ...
