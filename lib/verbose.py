from collections import defaultdict
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Callable, DefaultDict, Generic, Optional, Set, TypeVar, cast

from .problem import Problems
from .typing import SoundName


T = TypeVar("T")


class _ContextVarProperty(Generic[T]):
    _contextvar: ContextVar[Optional[T]]
    _constructor: Callable[[], T]
    _settable: bool

    def __init__(self, contextvar: ContextVar[Optional[T]], constructor: Callable[[], T], settable: bool = False):
        self._contextvar = contextvar
        self._constructor = constructor
        self._settable = settable

    def __get__(self, obj: Any, objtype: Any = None) -> T:
        if self._contextvar.get(None) is None:
            value = self._constructor()
            self._contextvar.set(value)
            return value
        return cast(T, self._contextvar.get())

    def __set__(self, obj: Any, value: T) -> None:
        if not self._settable:
            raise AttributeError
        self._contextvar.set(value)

    def __delete__(self, obj: Any) -> None:
        if not self._settable:
            raise AttributeError
        self._contextvar.set(None)


problems: ContextVar[Optional[Problems]] = ContextVar("problems")
files: ContextVar[Optional[DefaultDict[Path, Set[SoundName]]]] = ContextVar("files")


class _Verbose:
    problems = _ContextVarProperty(problems, list)
    files = _ContextVarProperty(files, lambda: defaultdict(set))


verbose = _Verbose()
