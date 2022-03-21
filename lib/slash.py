from pydantic import constr, root_validator
from typing import Any, Dict, NewType, Union

from .permissions import PermissionsOptionalMixin
from .sound import SoundRequiredMixin
from .types import DescriptionOptionalMixin, NameKeyDict, NamedMixin


# https://discord.com/developers/docs/interactions/application-commands#application-command-object
SlashNameType = constr(regex=r"^[\w-]{1,32}$")
# https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-option-choice-structure
SlashOptionType = constr(regex=r"^.{1,100}$")

SlashName = NewType("SlashName", SlashNameType)
SlashOption = NewType("SlashOption", SlashOptionType)


class CommonSlashCommand(
    NamedMixin[SlashName],
    PermissionsOptionalMixin,
):
    pass


class SlashCommand(
    CommonSlashCommand,
    SoundRequiredMixin,
    DescriptionOptionalMixin,
):
    pass


class SlashCommandOptionOption(SoundRequiredMixin):
    pass


class SlashOptionCommand(
    CommonSlashCommand,
    DescriptionOptionalMixin,
):
    options: Dict[SlashOption, SlashCommandOptionOption]
    default: SlashOption

    @root_validator()
    def check_default_exists(cls, values: Dict[str, Any]):
        if "default" in values and "options" in values:
            if values["default"] not in values["options"]:
                raise ValueError("Default not in options")
        return values


class SlashSubcommand(CommonSlashCommand):
    subcommands: "NameKeyDict[SlashName, AnySlashCommand]"


AnySlashCommand = Union[SlashCommand, SlashOptionCommand, SlashSubcommand]
SlashSubcommand.update_forward_refs()

COMMANDS_SLASH_JSON = NameKeyDict[SlashName, AnySlashCommand]
