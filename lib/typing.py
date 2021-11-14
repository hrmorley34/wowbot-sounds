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


class _DescriptionOptionalDef(TypedDict, total=False):
    description: str


CommandKwargType = NewType("CommandKwargType", Dict[str, Any])


class CommandDef(_SoundRequiredDef, _DescriptionOptionalDef, total=False):
    # sound: SoundName
    # description: str

    aliases: List[CommandAliasName]
    commandkwargs: CommandKwargType


class SlashCommandDef(_SoundRequiredDef, _DescriptionOptionalDef, total=False):
    # sound: SoundName
    # description: str
    pass


class SlashCommandOptionOption(_SoundRequiredDef):
    # sound: SoundName
    pass


class SlashCommandOptionDef(_DescriptionOptionalDef, total=True):
    # description: str

    options: Dict[SlashOption, SlashCommandOptionOption]
    default: SlashOption


SlashCommandCommon = Union[SlashCommandDef, SlashCommandOptionDef]


SOUNDS_JSON = Dict[SoundName, SoundDef]
COMMANDS_JSON = Dict[CommandName, CommandDef]
COMMANDS_SLASH_JSON = Dict[SlashGroup, Dict[SlashName, SlashCommandCommon]]
