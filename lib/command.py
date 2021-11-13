from typing import Dict, Optional, Set, cast

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


class BaseSlashCommand:
    name: SlashName
    group: Optional[SlashGroup]
    description: Optional[str]

    def __new__(cls, group: Optional[SlashGroup], name: SlashName, data: SlashCommandCommon, sounds: SoundDict):
        if cls is not BaseSlashCommand:
            return object.__new__(cls)

        if "options" in data:
            return SlashOptionCommand(group, name, cast(SlashCommandOptionDef, data), sounds=sounds)
        else:
            return SlashCommand(group, name, data, sounds=sounds)

    def __init__(self, group: Optional[SlashGroup], name: SlashName, data: SlashCommandCommon, sounds: SoundDict):
        raise NotImplementedError


class SlashCommand(BaseSlashCommand):
    sound: Sound

    def __init__(self, group: Optional[SlashGroup], name: SlashName, data: SlashCommandDef, sounds: SoundDict):
        self.name = name
        if not group:
            group = None
        self.group = group

        self.description = data.get("description")

        self.sound = sounds[data["sound"]]


class SlashOptionCommand(BaseSlashCommand):
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
