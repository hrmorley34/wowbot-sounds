from enum import Enum
import re
from typing import ClassVar, Dict, Optional, Type, cast

from .sound import Sound, SoundDict
from .types import (
    SlashCommandCommon,
    SlashCommandDef,
    SlashCommandOptionDef,
    SlashGroup,
    SlashName,
    SlashOption,
)


RE_APPLICATION_COMMAND = re.compile(r"^[\w-]{1,32}$")


class SlashCommandType(Enum):
    normal = "normal"
    options = "options"


class BaseSlashCommand:
    name: SlashName
    group: Optional[SlashGroup]
    description: Optional[str]

    _slashcommandtypes: ClassVar[Dict[SlashCommandType, Type["BaseSlashCommand"]]] = {}
    _is_base: ClassVar[bool] = True

    def __new__(
        cls,
        group: Optional[SlashGroup],
        name: SlashName,
        data: SlashCommandCommon,
        sounds: SoundDict,
    ):
        if not getattr(cls, "_is_base", False):
            return object.__new__(cls)

        if "options" in data:
            return cls._slashcommandtypes[SlashCommandType.options](
                group, name, cast(SlashCommandOptionDef, data), sounds=sounds
            )
        else:
            return cls._slashcommandtypes[SlashCommandType.normal](
                group, name, data, sounds=sounds
            )

    def __init_subclass__(
        cls, *, is_base: bool = False, slashtype: Optional[SlashCommandType] = None
    ):
        if is_base:
            cls._is_base = True
            cls._slashcommandtypes = {}
            if slashtype is not None:
                raise ValueError("Class with is_base cannot have a type")
        if slashtype is not None:
            cls._slashcommandtypes[slashtype] = cls
            cls._is_base = False

    def __init__(
        self,
        group: Optional[SlashGroup],
        name: SlashName,
        data: SlashCommandCommon,
        sounds: SoundDict,
    ):
        raise NotImplementedError


class SlashCommand(BaseSlashCommand, slashtype=SlashCommandType.normal):
    sound: Sound

    def __init__(
        self,
        group: Optional[SlashGroup],
        name: SlashName,
        data: SlashCommandDef,
        sounds: SoundDict,
    ):
        self.name = name
        if not group:
            group = None
        self.group = group

        self.description = data.get("description")

        self.sound = sounds[data["sound"]]


class SlashOptionCommand(BaseSlashCommand, slashtype=SlashCommandType.options):
    options: Dict[SlashOption, Sound]
    default: SlashOption

    def __init__(
        self,
        group: Optional[SlashGroup],
        name: SlashName,
        data: SlashCommandOptionDef,
        sounds: SoundDict,
    ):
        self.name = name
        if not group:
            group = None
        self.group = group

        self.description = data.get("description")

        self.options = dict()
        for opname, opdata in data["options"].items():
            self.options[opname] = sounds[opdata["sound"]]

        self.default = data["default"]
