import functools
import typing as t

from dddmisc.repository.repository import AbstractRepository

# P = t.ParamSpec('P')
R = t.TypeVar('R')


def getter(func):
    @functools.wraps(func)
    def wrapper(self: AbstractRepository, **kwargs):
        aggregate = next((aggregate for aggregate in self._seen
                          if aggregate.check_by_parameters(**kwargs)), None)
        if aggregate:
            return aggregate
        aggregate = func(self, **kwargs)
        self._seen.add(aggregate)
        return aggregate

    return wrapper


def agetter(func):

    @functools.wraps(func)
    async def wrapper(self: AbstractRepository, **kwargs):
        aggregate = next((aggregate for aggregate in self._seen
                          if aggregate.check_by_parameters(**kwargs)), None)
        if aggregate:
            return aggregate
        aggregate = await func(self, **kwargs)
        self._seen.add(aggregate)
        return aggregate

    return wrapper
