from collections import defaultdict
from contextvars import ContextVar
from pathlib import Path
from typing import DefaultDict, Optional, Set, Tuple

from .problem import Problems
from .types import CommandName, SlashGroup, SlashName, SoundName
from .utils import DefaultContextVarProperty


problems: ContextVar[Optional[Problems]] = ContextVar("problems")
files: ContextVar[Optional[DefaultDict[Path, Set[SoundName]]]] = ContextVar("files")
commandsounds: ContextVar[
    Optional[DefaultDict[SoundName, Set[CommandName]]]
] = ContextVar("commandsounds")
slashsounds: ContextVar[
    Optional[DefaultDict[SoundName, Set[Tuple[Optional[SlashGroup], SlashName]]]]
] = ContextVar("slashsounds")


class _Verbose:
    problems = DefaultContextVarProperty(problems, list)
    files = DefaultContextVarProperty(files, lambda: defaultdict(set))
    commandsounds = DefaultContextVarProperty(commandsounds, lambda: defaultdict(set))
    slashsounds = DefaultContextVarProperty(slashsounds, lambda: defaultdict(set))


verbose = _Verbose()
