__all__ = [
    "ContextType",
    "get_verbose",
    "set_verbose",
    "get_context",
    "context",
]

from contextvars import ContextVar
from typing import Any, Tuple

from .utils import ContextVarWithValue


_verbose: ContextVar[bool] = ContextVar("verbose")
ContextType = Tuple[Any, ...]
_context: ContextVar[ContextType] = ContextVar("context")


def get_verbose() -> bool:
    return _verbose.get(False)


def set_verbose(value: bool = True) -> None:
    _verbose.set(value)


def get_context() -> ContextType:
    return _context.get()


def context(*obj: Any) -> ContextVarWithValue[ContextType]:
    "Context manager for adding a context (for `Problem`s)"
    return ContextVarWithValue(_context, _context.get(()) + tuple(obj))
