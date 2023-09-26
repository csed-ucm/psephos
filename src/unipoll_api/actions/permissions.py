from unipoll_api.schemas import PolicySchemas
from unipoll_api.utils import Permissions


# Get All Workspace Permissions
async def get_workspace_permissions() -> PolicySchemas.PermissionList:
    permissions = Permissions.WORKSPACE_ALL_PERMISSIONS.name.split('|')  # type: ignore
    return PolicySchemas.PermissionList(permissions=permissions)


# Get all possible group permissions
async def get_group_permissions() -> PolicySchemas.PermissionList:
    permissions = Permissions.GROUP_ALL_PERMISSIONS.name.split('|')  # type: ignore
    return PolicySchemas.PermissionList(permissions=permissions)
