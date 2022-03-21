from collections import defaultdict
from typing import Dict, NewType, Set

from pydantic import validator

from .permissions import PermissionsOptionalMixin
from .sound import SoundRequiredMixin
from .types import DescriptionOptionalMixin, NameKeyDict, NamedMixin


AnyCommandName = NewType("CommandCommonName", str)
CommandName = NewType("CommandName", AnyCommandName)
CommandAliasName = NewType("CommandAliasName", AnyCommandName)


class Command(
    NamedMixin[CommandName],
    SoundRequiredMixin,
    DescriptionOptionalMixin,
    PermissionsOptionalMixin,
):
    aliases: Set[CommandAliasName] = set()


class COMMANDS_JSON(NameKeyDict[CommandName, Command]):
    @validator("__root__")
    def check_duplicate_names(cls, values: Dict[CommandName, Command]):
        uses_of_names: defaultdict[AnyCommandName, set[CommandName]] = defaultdict(set)

        for cmd in values.values():
            for name in (cmd.name, *cmd.aliases):
                uses_of_names[name].add(cmd.name)

        erroneous = {
            name: uses for name, uses in uses_of_names.items() if len(uses) > 1
        }

        if len(erroneous) > 0:
            raise ValueError(f"Reuse of names: {erroneous}")

        return values
