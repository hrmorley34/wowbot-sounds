__all__ = [
    "SlashTracker",
    "SlashCommandType",
    "BaseSlashCommand",
    "SlashCommand",
    "SlashOptionCommand",
    "SlashSubcommandCommand",
]

from collections import defaultdict
from contextvars import ContextVar
from enum import Enum
import re
from typing import (
    Any,
    ClassVar,
    DefaultDict,
    Dict,
    Generic,
    Optional,
    Set,
    Type,
    cast,
)

from .permissions import Permissions, get_permissions
from .problem import Problem
from .sound import Sound, SoundT, SoundTDict
from .types import (
    COMMANDS_SLASH_JSON,
    AnySlashCommandDef,
    SlashCommandDef,
    SlashCommandOptionDef,
    SlashName,
    SlashOption,
    SlashSubcommandDef,
)
from .utils import DefaultContextVarProperty
from .verbose import context


RE_APPLICATION_COMMAND = re.compile(r"^[\w-]{1,32}$")


_SlashCommands = DefaultDict["Sound", Set["BaseSlashCommand[Any]"]]
_slashsounds: ContextVar[Optional[_SlashCommands]] = ContextVar("slashsounds")


class _SlashTracker:
    slashsounds = DefaultContextVarProperty(_slashsounds, lambda: defaultdict(set))


SlashTracker = _SlashTracker()


class SlashCommandType(Enum):
    normal = "normal"
    options = "options"
    subcommand = "subcommand"


class BaseSlashCommand(Generic[SoundT]):
    registry: ClassVar[Dict[SlashCommandType, Type["BaseSlashCommand[Any]"]]] = dict()
    base_type: ClassVar[Type["BaseSlashCommand[Any]"]]

    name: SlashName
    parent: Optional["SlashSubcommandCommand[SoundT]"]

    default_permission: bool
    permissions: Permissions

    @staticmethod
    def get_type(data: AnySlashCommandDef) -> SlashCommandType:
        if "subcommands" in data:
            return SlashCommandType.subcommand
        elif "options" in data:
            return SlashCommandType.options
        else:
            return SlashCommandType.normal

    def __new__(
        cls,
        parent: Optional["SlashSubcommandCommand[SoundT]"],
        name: SlashName,
        data: AnySlashCommandDef,
        sounds: SoundTDict[SoundT],
    ):
        if getattr(cls, "_base_type", None) is not cls:
            return object.__new__(cls)

        subcls = cls.registry[cls.get_type(data)]
        return subcls(parent, name, data, sounds=sounds)

    def __init_subclass__(
        cls, *, is_base: bool = False, slashtype: Optional[SlashCommandType] = None
    ) -> None:
        if is_base:
            cls.base_type = cls
            cls.registry = {}
            if slashtype is not None:
                raise ValueError("Class with is_base cannot have a type")
        if slashtype is not None:
            cls.registry[slashtype] = cls

    def __init__(
        self,
        parent: Optional["SlashSubcommandCommand[SoundT]"],
        name: SlashName,
        data: AnySlashCommandDef,
        sounds: SoundTDict[SoundT],
    ):
        if (
            parent is not None
            and parent.parent is not None
            and parent.parent.parent is not None
        ):
            raise ValueError("Max parent depth is 2")
        if not RE_APPLICATION_COMMAND.match(name):
            raise ValueError(
                f"Name must match regular expression: {RE_APPLICATION_COMMAND.pattern}"
            )
        self.name = name
        self.parent = parent

        self.default_permission, self.permissions = get_permissions(data)

    @classmethod
    def init_verbose(
        cls,
        parent: Optional["SlashSubcommandCommand[SoundT]"],
        name: SlashName,
        data: AnySlashCommandDef,
        sounds: SoundTDict[SoundT],
    ) -> "BaseSlashCommand[SoundT]":
        subcls = cls.registry[cls.get_type(data)]
        return subcls.init_verbose(parent, name, data, sounds=sounds)

    def __hash__(self) -> int:
        return hash((type(self), self.parent, self.name))

    def __repr__(self) -> str:
        return "<" + type(self).__name__ + f" parent={self.parent!r} {self.name!r}>"

    @classmethod
    def from_json(
        cls, slash_commands_json: COMMANDS_SLASH_JSON, sounds: SoundTDict[SoundT]
    ) -> Dict[SlashName, "BaseSlashCommand[SoundT]"]:
        commands: Dict[SlashName, BaseSlashCommand[SoundT]] = dict()

        for name, data in slash_commands_json.items():
            with context(f"Slashcommand {name!r}") as ctx:
                try:
                    command = BaseSlashCommand.init_verbose(
                        None, name, data, sounds=sounds
                    )
                except KeyError as e:
                    Problem(f"Missing key {e.args[0]}").add()
                    continue
                # except Exception as e:
                #     verbose.problems.append(Problem(f"{e!r}", context=f"Slashcommand {group!r}.{name!r}"))
                #     continue
                else:
                    ctx.set(ctx.get()[:-1] + (command,))

                    commands[name] = command

        return commands


BaseSlashCommand.base_type = BaseSlashCommand


class SlashCommand(BaseSlashCommand[SoundT], slashtype=SlashCommandType.normal):
    sound: Sound

    def __init__(
        self,
        parent: Optional["SlashSubcommandCommand[SoundT]"],
        name: SlashName,
        data: SlashCommandDef,
        sounds: SoundTDict[SoundT],
    ):
        super().__init__(parent, name, data, sounds=sounds)

        self.description = data.get("description")

        self.sound = sounds[data["sound"]]

    @classmethod
    def init_verbose(
        cls,
        parent: Optional["SlashSubcommandCommand[SoundT]"],
        name: SlashName,
        data: AnySlashCommandDef,
        sounds: SoundTDict[SoundT],
    ) -> "BaseSlashCommand[SoundT]":
        data = cast(SlashCommandDef, data)
        self = cls(parent, name, data, sounds=sounds)

        SlashTracker.slashsounds[self.sound].add(self)
        return self


class SlashOptionCommand(BaseSlashCommand[SoundT], slashtype=SlashCommandType.options):
    options: Dict[SlashOption, Sound]
    default: SlashOption

    def __init__(
        self,
        parent: Optional["SlashSubcommandCommand[SoundT]"],
        name: SlashName,
        data: SlashCommandOptionDef,
        sounds: SoundTDict[SoundT],
    ):
        super().__init__(parent, name, data, sounds=sounds)

        self.description = data.get("description")

        self.options = dict()
        for opname, opdata in data["options"].items():
            self.options[opname] = sounds[opdata["sound"]]

        self.default = data["default"]

    @classmethod
    def init_verbose(
        cls,
        parent: Optional["SlashSubcommandCommand[SoundT]"],
        name: SlashName,
        data: AnySlashCommandDef,
        sounds: SoundTDict[SoundT],
    ) -> "BaseSlashCommand[SoundT]":
        data = cast(SlashCommandOptionDef, data)
        self = cls(parent, name, data, sounds=sounds)

        with context(self):
            for sound in self.options.values():
                SlashTracker.slashsounds[sound].add(self)
            if self.default not in self.options:
                Problem(f"Invalid default sound {self.default!r}").add()
            return self


class SlashSubcommandCommand(
    BaseSlashCommand[SoundT], slashtype=SlashCommandType.subcommand
):
    subcommands: Dict[SlashName, BaseSlashCommand[SoundT]]

    def __init__(
        self,
        parent: Optional["SlashSubcommandCommand[SoundT]"],
        name: SlashName,
        data: SlashSubcommandDef,
        sounds: SoundTDict[SoundT],
    ):
        super().__init__(parent, name, data, sounds=sounds)

        self.subcommands = {}
        for subname, subdata in data["subcommands"].items():
            self.subcommands[subname] = BaseSlashCommand(
                self, subname, subdata, sounds=sounds
            )

    @classmethod
    def init_verbose(
        cls,
        parent: Optional["SlashSubcommandCommand[SoundT]"],
        name: SlashName,
        data: AnySlashCommandDef,
        sounds: SoundTDict[SoundT],
    ) -> "BaseSlashCommand[SoundT]":
        data = cast(SlashSubcommandDef, data)
        self = object.__new__(cls)
        super(__class__, self).__init__(parent, name, data, sounds=sounds)

        self.subcommands = {}
        for subname, subdata in data["subcommands"].items():
            self.subcommands[subname] = BaseSlashCommand.init_verbose(
                self, subname, subdata, sounds=sounds
            )

        return self
