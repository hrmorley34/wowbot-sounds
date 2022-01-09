__all__ = [
    "Problem",
    "Problems",
    "ProblemTracker",
]

from contextvars import ContextVar
from typing import Any, List, Optional, Tuple

from .utils import DefaultContextVarProperty
from .verbose import get_context, get_verbose


class Problem(Exception):
    problem: str
    context: Tuple[object]

    def __init__(self, problem: str, context: Tuple[Any, ...] = ()):
        self.problem = problem
        self.context = get_context() + context
        super().__init__(str(self))

    def __str__(self) -> str:
        return ":".join(map(str, self.context)) + f": {self.problem}"

    def add(self) -> None:
        ProblemTracker.problems.append(self)
        if get_verbose():
            print(str(self))
        else:
            raise self

    @staticmethod
    def get_problems() -> "Problems":
        return ProblemTracker.problems


Problems = List[Problem]

problems: ContextVar[Optional[Problems]] = ContextVar("problems")


class _ProblemTracker:
    problems = DefaultContextVarProperty(problems, list)


ProblemTracker = _ProblemTracker()
