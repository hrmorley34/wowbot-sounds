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
    "PermissionDef",
    "PermissionsDef",
    "PermissionsOptionalMixin",
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

from typing import Dict, List, NewType, TypeVar, TypedDict, Union
from typing_extensions import Literal


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


PERMISSION_TYPE_ROLE = "role"
PERMISSION_TYPE_USER = "user"
PermissionType = Literal["role", "user"]


class _PartialPermissionDef(TypedDict, total=False):
    state: bool


class PermissionDef(_PartialPermissionDef, total=True):
    type: PermissionType
    ids: List[int]


PermissionsDef = List[PermissionDef]


class PermissionsOptionalMixin(TypedDict, total=False):
    default_permission: bool
    permissions: PermissionsDef


class CommandDef(
    SoundRequiredMixin, DescriptionOptionalMixin, PermissionsOptionalMixin, total=False
):
    # sound: SoundName
    # description: str

    aliases: List[CommandAliasName]


class SlashCommandDef(
    SoundRequiredMixin, DescriptionOptionalMixin, PermissionsOptionalMixin, total=False
):
    # sound: SoundName
    # description: str
    pass


class SlashCommandOptionOption(SoundRequiredMixin):
    # sound: SoundName
    pass


class SlashCommandOptionDef(
    DescriptionOptionalMixin, PermissionsOptionalMixin, total=True
):
    # description: str

    options: Dict[SlashOption, SlashCommandOptionOption]
    default: SlashOption


class SlashSubcommandDef(PermissionsOptionalMixin, total=True):
    subcommands: Dict[SlashName, "AnySlashCommandDef"]


AnySlashCommandDef = Union[SlashCommandDef, SlashCommandOptionDef, SlashSubcommandDef]


SOUNDS_JSON = Dict[SoundName, SoundDef]
COMMANDS_JSON = Dict[CommandName, CommandDef]
COMMANDS_SLASH_JSON = Dict[SlashName, AnySlashCommandDef]
