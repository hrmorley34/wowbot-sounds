from enum import Enum
from typing import List, Set, Tuple

from .problem import Problem
from .types import (
    PERMISSION_TYPE_ROLE,
    PERMISSION_TYPE_USER,
    PermissionDef,
    PermissionsOptionalMixin,
)


class PermissionType(Enum):
    ROLE = PERMISSION_TYPE_ROLE
    USER = PERMISSION_TYPE_USER


class Permission:
    type: PermissionType
    ids: Set[int]
    state: bool

    def __init__(self, data: PermissionDef) -> None:
        self.type = PermissionType(data["type"])
        self.ids = set(map(int, data["ids"]))
        self.state = bool(data.get("state", True))

        if not len(self.ids):
            Problem("No ids supplied to permission", context=(self,)).add()

    def __repr__(self) -> str:
        return f"<Permission {self.type} ids={self.ids} state={self.state}>"


Permissions = List[Permission]


def get_permissions(data: PermissionsOptionalMixin) -> Tuple[bool, Permissions]:
    has_permissions = "permissions" in data

    default_permission = data.get("default_permission", not has_permissions)
    permissions = [Permission(p) for p in data.get("permissions", [])]

    return default_permission, permissions
