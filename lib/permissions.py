from enum import Enum
from pydantic import conset, root_validator
from typing import Any, Dict, List

from .types import BaseModel


class PermissionType(Enum):
    role = "role"
    user = "user"


NonEmptyIntSet = conset(int, min_items=1)


class Permission(BaseModel):
    type: PermissionType
    ids: NonEmptyIntSet
    state: bool = True


Permissions = List[Permission]


class PermissionsOptionalMixin(BaseModel):
    default_permission: bool = ...  # type: ignore
    permissions: Permissions = ...  # type: ignore

    @root_validator(pre=True)
    def check_permissions(cls, data: Dict[str, Any]):
        data = data.copy()

        if "permissions" not in data:
            data["permissions"] = []
            has_permissions = False
        else:
            has_permissions = True

        if data.get("default_permission") is None:
            data["default_permission"] = not has_permissions

        return data
