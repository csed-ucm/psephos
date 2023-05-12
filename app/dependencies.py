from fastapi import Depends, Request
from app.account_manager import current_active_user, get_current_active_user
from app.models.documents import ResourceID, Workspace, Group, Account
from app.utils import permissions as Permissions
# Exceptions
from app.exceptions import workspace as WorkspaceExceptions
from app.exceptions import group as GroupExceptions
from app.utils.path_operations import extract_action_from_path, extract_resourceID_from_path


# Dependency for getting a workspace with the given id
async def get_workspace_model(workspace_id: ResourceID) -> Workspace:
    """
    Returns a workspace with the given id.
    """
    workspace = await Workspace.get(workspace_id)
    if not workspace:
        raise WorkspaceExceptions.WorkspaceNotFound(workspace_id)
    return workspace


# Dependency to get a group by id and verify it exists
async def get_group_model(group_id: ResourceID) -> Group:
    """
    Returns a group with the given id.
    """
    workspace = await Group.get(group_id)
    if not workspace:
        raise GroupExceptions.GroupNotFound(group_id)
    return workspace


# Dependency to get a user by id and verify it exists
async def set_active_user(user_account: Account = Depends(get_current_active_user)):
    current_active_user.set(user_account)
    return user_account


# Check if the current user has permissions to access the workspace and perform requested actions
async def check_workspace_permission(request: Request, account: Account = Depends(get_current_active_user)):
    # Extract requested action(operationID) and id of the workspace from the path
    operationID = extract_action_from_path(request)
    workspaceID = extract_resourceID_from_path(request)

    # Get the workspace with the given id
    workspace = await Workspace.get(workspaceID, fetch_links=True)

    # Check if workspace exists
    if not workspace:
        raise WorkspaceExceptions.WorkspaceNotFound(workspaceID)

    # Get the user policy for the workspace
    user_permissions = await Permissions.get_all_permissions(workspace, account)

    # Check that the user has the required permission
    try:
        required_permission = Permissions.WorkspacePermissions[operationID]  # type: ignore
        if not Permissions.check_permission(Permissions.WorkspacePermissions(user_permissions), required_permission):
            raise WorkspaceExceptions.UserNotAuthorized(account, workspace, operationID)
    except KeyError:
        raise WorkspaceExceptions.ActionNotFound(operationID)


# Check if the current user has permissions to access the workspace and perform requested actions
async def check_group_permission(request: Request, account: Account = Depends(get_current_active_user)):
    # Extract requested action(operationID) and id of the workspace from the path
    operationID = extract_action_from_path(request)
    groupID = extract_resourceID_from_path(request)
    # Get the workspace with the given id
    group = await Group.get(groupID, fetch_links=True)
    # Check if workspace exists
    if not group:
        raise GroupExceptions.GroupNotFound(groupID)
    # Get the user policy for the workspace
    # print(group.members)
    user_permissions = await Permissions.get_all_permissions(group, account)

    # Check that the user has the required permission
    try:
        required_permission = Permissions.GroupPermissions[operationID]  # type: ignore
        if not Permissions.check_permission(Permissions.GroupPermissions(user_permissions), required_permission):
            raise GroupExceptions.UserNotAuthorized(account, group, operationID)
    except KeyError:
        raise GroupExceptions.ActionNotFound(operationID)
