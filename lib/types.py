__all__ = [
    "SoundName",
    "AnyCommandName",
    "CommandName",
    "CommandAliasName",
    "SlashName",
    "SlashOption",
    "SoundPath",
    "SoundDef",
    "SoundRequiredMixin",
    "DescriptionOptionalMixin",
    "CommandKwargType",
    "CommandDef",
    "SlashCommandDef",
    "SlashCommandOptionOption",
    "SlashCommandOptionDef",
    "SlashSubcommandDef",
    "AnySlashCommandDef",
    "SOUNDS_JSON",
    "COMMANDS_JSON",
    "COMMANDS_SLASH_JSON",
]

from typing import Any, Dict, List, NewType, TypeVar, TypedDict, Union


T = TypeVar("T")


SoundName = NewType("SoundName", str)
AnyCommandName = NewType("CommandCommonName", str)
CommandName = NewType("CommandName", AnyCommandName)
CommandAliasName = NewType("CommandAliasName", AnyCommandName)
SlashName = NewType("SlashName", str)
SlashOption = NewType("SlashOption", str)


class SoundPath(TypedDict, total=False):
    glob: str
    filenames: List[str]
    filename: str
    weight: int


SoundDef = List[SoundPath]


class SoundRequiredMixin(TypedDict, total=True):
    sound: SoundName


class DescriptionOptionalMixin(TypedDict, total=False):
    description: str


CommandKwargType = NewType("CommandKwargType", Dict[str, Any])


class CommandDef(SoundRequiredMixin, DescriptionOptionalMixin, total=False):
    # sound: SoundName
    # description: str

    aliases: List[CommandAliasName]
    commandkwargs: CommandKwargType


class SlashCommandDef(SoundRequiredMixin, DescriptionOptionalMixin, total=False):
    # sound: SoundName
    # description: str
    pass


class SlashCommandOptionOption(SoundRequiredMixin):
    # sound: SoundName
    pass


class SlashCommandOptionDef(DescriptionOptionalMixin, total=True):
    # description: str

    options: Dict[SlashOption, SlashCommandOptionOption]
    default: SlashOption


class SlashSubcommandDef(TypedDict, total=True):
    subcommands: Dict[SlashName, "AnySlashCommandDef"]


AnySlashCommandDef = Union[SlashCommandDef, SlashCommandOptionDef, SlashSubcommandDef]


SOUNDS_JSON = Dict[SoundName, SoundDef]
COMMANDS_JSON = Dict[CommandName, CommandDef]
COMMANDS_SLASH_JSON = Dict[SlashName, AnySlashCommandDef]
