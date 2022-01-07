from typing import Optional, Set, cast

from .sound import Sound, SoundDict
from .types import CommandAliasName, CommandDef, CommandKwargType, CommandName


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
