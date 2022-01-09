__all__ = [
    "CommandTracker",
    "Command",
]

from collections import defaultdict
from contextvars import ContextVar
from typing import Any, DefaultDict, Dict, Generic, Optional, Set, cast

from .problem import Problem
from .sound import Sound, SoundT, SoundTDict
from .types import (
    COMMANDS_JSON,
    AnyCommandName,
    CommandAliasName,
    CommandDef,
    CommandKwargType,
    CommandName,
)
from .utils import DefaultContextVarProperty
from .verbose import context


_CommandSounds = DefaultDict["Sound", Set["Command[Any]"]]
_commandsounds: ContextVar[Optional[_CommandSounds]] = ContextVar("commandsounds")


class _CommandTracker:
    commandsounds = DefaultContextVarProperty(_commandsounds, lambda: defaultdict(set))


CommandTracker = _CommandTracker()


class Command(Generic[SoundT]):
    name: CommandName
    sound: SoundT
    aliases: Set[CommandAliasName]
    description: Optional[str]
    commandkwargs: CommandKwargType

    def __init__(self, name: CommandName, data: CommandDef, sounds: SoundTDict[SoundT]):
        self.name = name

        self.sound = sounds[data["sound"]]

        self.aliases = set(data.get("aliases", ()))
        self.aliases.discard(cast(CommandAliasName, name))

        self.description = data.get("description")

        self.commandkwargs = data.get("commandkwargs", {})

    def __hash__(self) -> int:
        return hash((type(self), self.name, self.sound))

    def __repr__(self) -> str:
        return (
            "<"
            + type(self).__name__
            + f" {self.name!r} sound={self.sound!r} aliases={self.aliases!r} description={self.description!r}>"
        )

    @classmethod
    def from_json(
        cls, commands_json: COMMANDS_JSON, sounds: SoundTDict[SoundT]
    ) -> Dict[CommandName, "Command[SoundT]"]:
        commands: Dict[CommandName, Command[SoundT]] = dict()
        aliases: Set[AnyCommandName] = set()

        for name, data in commands_json.items():
            with context(f"Command {name!r}") as ctx:
                if name in aliases:
                    Problem(f"Reuse of name {name!r}").add()
                aliases.add(name)

                try:
                    cmd = Command(name, data, sounds=sounds)
                except KeyError as e:
                    Problem(f"Missing key {e.args[0]}").add()
                    continue
                # except Exception as e:
                #     verbose.problems.append(Problem(f"{e!r}", context=f"Command {name!r}"))
                #     continue
                else:
                    ctx.set(ctx.get()[:-1] + (cmd,))

                    commands[name] = cmd
                    CommandTracker.commandsounds[cmd.sound].add(cmd)
                    for a in cmd.aliases:
                        if a in aliases:
                            Problem(f"Reuse of alias {a!r}").add()
                        aliases.add(a)

        return commands
