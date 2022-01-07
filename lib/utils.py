from contextvars import ContextVar
from typing import Any, Callable, Generic, Optional, TypeVar


T = TypeVar("T")


class ContextVarProperty(Generic[T]):
    _contextvar: ContextVar[T]
    _settable: bool

    def __init__(
        self,
        contextvar: ContextVar[T],
        settable: bool = False,
    ):
        self._contextvar = contextvar
        self._settable = settable

    def __get__(self, obj: Any, objtype: Any = None) -> T:
        return self._contextvar.get()

    def __set__(self, obj: Any, value: T) -> None:
        if not self._settable:
            raise AttributeError
        self._contextvar.set(value)

    def __delete__(self, obj: Any) -> None:
        raise AttributeError


class DefaultContextVarProperty(Generic[T], ContextVarProperty[Optional[T]]):
    _default_constructor: Callable[[], T]

    def __init__(
        self,
        contextvar: ContextVar[Optional[T]],
        default_constructor: Callable[[], T],
        settable: bool = False,
    ):
        super().__init__(contextvar=contextvar, settable=settable)
        self._default_constructor = default_constructor

    def __get__(self, obj: Any, objtype: Any = None) -> T:
        value = self._contextvar.get(None)
        if value is None:
            value = self._default_constructor()
            self._contextvar.set(value)
        return value

    def __set__(self, obj: Any, value: T) -> None:
        return super().__set__(obj, value)

    def __delete__(self, obj: Any) -> None:
        if not self._settable:
            raise AttributeError
        self._contextvar.set(None)
