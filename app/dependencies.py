from fastapi import Depends, Request, HTTPException
from app.account_manager import current_active_user, get_current_active_user
from app.models.documents import ResourceID, Workspace, Group, Account
from app.utils import permissions as Permissions
# Exceptions
from app.exceptions import workspace as WorkspaceExceptions
from app.exceptions import group as GroupExceptions
from app.exceptions import account as AccountExceptions
from app.utils.path_operations import extract_action_from_path, extract_resourceID_from_path


# Dependency to get account by id
async def get_account(account_id: ResourceID) -> Account:
    """
    Returns an account with the given id.
    """
    account = await Account.get(account_id)
    if not account:
        raise AccountExceptions.AccountNotFound(account_id)
    return account


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
        e = WorkspaceExceptions.WorkspaceNotFound(workspaceID)
        raise HTTPException(e.code, str(e))

    if account.is_superuser:
        return

    # Get the user policy for the workspace
    user_permissions = await Permissions.get_all_permissions(workspace, account)

    # Check that the user has the required permission
    try:
        required_permission = Permissions.WorkspacePermissions[operationID]  # type: ignore
        if not Permissions.check_permission(Permissions.WorkspacePermissions(user_permissions),   # type: ignore
                                            required_permission):
            e = WorkspaceExceptions.UserNotAuthorized(account, workspace, operationID)
            raise HTTPException(e.code, str(e))
    except KeyError:
        e = WorkspaceExceptions.ActionNotFound(operationID)
        raise HTTPException(e.code, str(e))


# Check if the current user has permissions to access the workspace and perform requested actions
async def check_group_permission(request: Request, account: Account = Depends(get_current_active_user)):
    # Extract requested action(operationID) and id of the workspace from the path
    operationID = extract_action_from_path(request)
    groupID = extract_resourceID_from_path(request)
    # Get the workspace with the given id
    group = await Group.get(ResourceID(groupID), fetch_links=True)
    # Check if workspace exists
    if not group:
        e = GroupExceptions.GroupNotFound(groupID)
        raise HTTPException(e.code, str(e))
    # Get the user policy for the workspace
    # print(group.members)
    user_permissions = await Permissions.get_all_permissions(group, account)

    # Check that the user has the required permission
    try:
        required_permission = Permissions.GroupPermissions[operationID]  # type: ignore
        if not Permissions.check_permission(Permissions.GroupPermissions(user_permissions),  # type: ignore
                                            required_permission):
            e = GroupExceptions.UserNotAuthorized(account, group, operationID)
            raise HTTPException(e.code, str(e))
    except KeyError:
        e = GroupExceptions.ActionNotFound(operationID)
        raise HTTPException(e.code, str(e))
