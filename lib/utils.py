__all__ = [
    "ContextVarProperty",
    "DefaultContextVarProperty",
    "ContextVarWithValue",
]

from contextvars import ContextVar, Token
from types import TracebackType
from typing import (
    Any,
    Callable,
    ContextManager,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
)


class _DefaultType:
    _obj: Optional["_DefaultType"] = None

    def __new__(cls) -> "_DefaultType":
        if cls._obj is None:
            cls._obj = super().__new__(cls)
        return cls._obj


_Default = _DefaultType()


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


_SubT = TypeVar("_SubT", bound="ContextVarWithValue[Any]")


class ContextVarWithValue(ContextManager[T], Generic[T]):
    _var: ContextVar[T]
    _value: Union[T, _DefaultType]
    _token: Optional["Token[T]"]
    _entered: bool
    _exited: bool

    def __init__(
        self, var: ContextVar[T], value: Union[T, _DefaultType] = _Default
    ) -> None:
        super().__init__()

        self._var = var
        self._value = value
        self._token = None
        self._entered = False
        self._exited = False

    def __enter__(self: _SubT) -> _SubT:
        assert not self._entered and not self._exited
        if not isinstance(self._value, _DefaultType):
            self._token = self._var.set(self._value)
        self._entered = True
        return self

    def get(self) -> T:
        return self._var.get()

    def set(self, value: T) -> None:
        assert self._entered and not self._exited
        token = self._var.set(value)
        if self._token is None:
            self._token = token

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        assert self._entered and not self._exited
        if self._token is not None:
            self._var.reset(self._token)
        self._exited = True
        return super().__exit__(exc_type, exc_value, traceback)
