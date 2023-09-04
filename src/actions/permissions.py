from src.schemas import policy as PolicySchemas
from src.utils import permissions as Permissions


# Get All Workspace Permissions
async def get_workspace_permissions() -> PolicySchemas.PermissionList:
    return PolicySchemas.PermissionList(permissions=Permissions.WORKSPACE_ALL_PERMISSIONS.name.split('|'))


# Get all possible group permissions
async def get_group_permissions() -> PolicySchemas.PermissionList:
    return PolicySchemas.PermissionList(permissions=Permissions.GROUP_ALL_PERMISSIONS.name.split('|'))
