from typing import Any, Dict, List, NewType, TypedDict, Union


SoundName = NewType("SoundName", str)
CommandCommonName = NewType("CommandCommonName", str)
CommandName = NewType("CommandName", CommandCommonName)
CommandAliasName = NewType("CommandAliasName", CommandCommonName)
SlashGroup = NewType("SlashGroup", str)
SlashName = NewType("SlashName", str)
SlashOption = NewType("SlashOption", str)


class SoundPath(TypedDict, total=False):
    glob: str
    filenames: List[str]
    filename: str
    weight: int


SoundDef = List[SoundPath]


class _SoundRequiredDef(TypedDict, total=True):
    sound: SoundName


class CommandDef(_SoundRequiredDef, total=False):
    # sound: SoundName

    aliases: List[CommandAliasName]
    description: str
    commandkwargs: Dict[str, Any]


class SlashCommandDef(_SoundRequiredDef, total=False):
    # sound: SoundName

    description: str


class SlashCommandOptionDef(TypedDict, total=True):
    options: Dict[SlashOption, SlashCommandDef]
    default: SlashOption


SlashCommandCommon = Union[SlashCommandDef, SlashCommandOptionDef]


SOUNDS_JSON = Dict[SoundName, SoundDef]
COMMANDS_JSON = Dict[CommandName, CommandDef]
COMMANDS_SLASH_JSON = Dict[SlashGroup, Dict[SlashName, SlashCommandCommon]]
