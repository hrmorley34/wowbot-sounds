from enum import Enum
from typing import Dict, Optional, Set, Type, cast

from .sound import Sound, SoundDict
from .typing import CommandAliasName, CommandDef, CommandKwargType, CommandName, SlashCommandCommon, SlashCommandDef, SlashCommandOptionDef, SlashGroup, SlashName, SlashOption


class Command:
    name: CommandName
    sound: Sound
    aliases: Set[CommandAliasName]
    description: Optional[str]
    commandkwargs: CommandKwargType

    def __init__(self, name: CommandName, data: CommandDef, sounds: SoundDict):
        self.name = name

        self.sound = sounds[data["sound"]]

        self.aliases = set(data.get("aliases", ()))
        self.aliases.discard(cast(CommandAliasName, name))

        self.description = data.get("description")

        self.commandkwargs = data.get("commandkwargs", {})


class SlashCommandType(Enum):
    normal = "normal"
    options = "options"


class BaseSlashCommand:
    name: SlashName
    group: Optional[SlashGroup]
    description: Optional[str]

    _slashcommandtypes: Dict[SlashCommandType, Type["BaseSlashCommand"]] = {}

    def __new__(cls, group: Optional[SlashGroup], name: SlashName, data: SlashCommandCommon, sounds: SoundDict):
        if cls is not BaseSlashCommand:
            return object.__new__(cls)

        if "options" in data:
            return cls._slashcommandtypes[SlashCommandType.options](group, name, cast(SlashCommandOptionDef, data), sounds=sounds)
        else:
            return cls._slashcommandtypes[SlashCommandType.normal](group, name, data, sounds=sounds)

    def __init_subclass__(cls, *, slashtype: Optional[SlashCommandType] = None):
        if slashtype is not None:
            cls._slashcommandtypes[slashtype] = cls

    def __init__(self, group: Optional[SlashGroup], name: SlashName, data: SlashCommandCommon, sounds: SoundDict):
        raise NotImplementedError


class SlashCommand(BaseSlashCommand, slashtype=SlashCommandType.normal):
    sound: Sound

    def __init__(self, group: Optional[SlashGroup], name: SlashName, data: SlashCommandDef, sounds: SoundDict):
        self.name = name
        if not group:
            group = None
        self.group = group

        self.description = data.get("description")

        self.sound = sounds[data["sound"]]


class SlashOptionCommand(BaseSlashCommand, slashtype=SlashCommandType.options):
    options: Dict[SlashOption, Sound]
    default: SlashOption

    def __init__(self, group: Optional[SlashGroup], name: SlashName, data: SlashCommandOptionDef, sounds: SoundDict):
        self.name = name
        if not group:
            group = None
        self.group = group

        self.description = data.get("description")

        self.options = dict()
        for opname, opdata in data["options"].items():
            self.options[opname] = sounds[opdata["sound"]]

        self.default = data["default"]
