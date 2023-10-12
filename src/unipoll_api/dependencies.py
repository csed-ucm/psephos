from typing import Annotated
from fastapi import Cookie, Depends, Query, Request, HTTPException, WebSocket
from unipoll_api.account_manager import active_user, get_current_active_user
from unipoll_api.documents import ResourceID, Workspace, Group, Account, Poll, Policy
from unipoll_api.utils import permissions as Permissions
from unipoll_api import exceptions as Exceptions
from unipoll_api.utils.path_operations import extract_action_from_path, extract_resourceID_from_path


# Dependency to get account by id
async def get_account(account_id: ResourceID) -> Account:
    """
    Returns an account with the given id.
    """
    account = await Account.get(account_id)
    if not account:
        raise Exceptions.AccountExceptions.AccountNotFound(account_id)
    return account


async def websocket_auth(websocket: WebSocket,
                         session: Annotated[str | None, Cookie()] = None,
                         token: Annotated[str | None, Query()] = None) -> dict:
    return {"cookie": session, "token": token}


# Dependency for getting a workspace with the given id
async def get_workspace(workspace_id: ResourceID) -> Workspace:
    """
    Returns a workspace with the given id.
    """
    workspace = await Workspace.get(workspace_id, fetch_links=True)

    if workspace:
        # await workspace.fetch_all_links()
        return workspace
    raise Exceptions.WorkspaceExceptions.WorkspaceNotFound(workspace_id)


# Dependency to get a group by id and verify it exists
async def get_group(group_id: ResourceID) -> Group:
    """
    Returns a group with the given id.
    """
    group = await Group.get(group_id, fetch_links=True)
    if group:
        # await group.fetch_all_links()
        return group
    raise Exceptions.GroupExceptions.GroupNotFound(group_id)


# Dependency to get a poll by id and verify it exists
async def get_poll(poll_id: ResourceID) -> Poll:
    """
    Returns a poll with the given id.
    """
    poll = await Poll.get(poll_id, fetch_links=True)
    if poll:
        return poll
    raise Exceptions.GroupExceptions.GroupNotFound(poll_id)


# Dependency to get a policy by id and verify it exists
async def get_policy(policy_id: ResourceID) -> Policy:
    policy = await Policy.get(policy_id, fetch_links=True)
    if policy:
        # await policy.parent_resource.fetch_all_links()  # type: ignore
        return policy
    raise Exceptions.PolicyExceptions.PolicyNotFound(policy_id)


# Dependency to get a user by id and verify it exists
async def set_active_user(user_account: Account = Depends(get_current_active_user)):
    active_user.set(user_account)
    return user_account


# Check if the current user has permissions to access the workspace and perform requested actions
async def check_workspace_permission(request: Request, account: Account = Depends(get_current_active_user)):
    # Extract requested action(operationID) and id of the workspace from the path
    operationID = extract_action_from_path(request)
    workspaceID = extract_resourceID_from_path(request)

    # Get the workspace with the given id
    workspace = await Workspace.get(workspaceID, fetch_links=True)

    e: Exception

    # Check if workspace exists
    if not workspace:
        e = Exceptions.WorkspaceExceptions.WorkspaceNotFound(workspaceID)
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
            e = Exceptions.WorkspaceExceptions.UserNotAuthorized(account, workspace, operationID)
            raise HTTPException(e.code, str(e))
    except KeyError:
        e = Exceptions.WorkspaceExceptions.ActionNotFound(operationID)
        raise HTTPException(e.code, str(e))


# Check if the current user has permissions to access the workspace and perform requested actions
async def check_group_permission(request: Request, account: Account = Depends(get_current_active_user)):
    # Extract requested action(operationID) and id of the workspace from the path
    operationID = extract_action_from_path(request)
    groupID = extract_resourceID_from_path(request)
    # Get the group with the given id
    group = await Group.get(ResourceID(groupID), fetch_links=True)
    # Check if group exists
    e: Exception
    if not group:
        e = Exceptions.GroupExceptions.GroupNotFound(groupID)
        raise HTTPException(e.code, str(e))
    # Get the user policy for the group
    # print(group.members)
    user_permissions = await Permissions.get_all_permissions(group, account)

    # Check that the user has the required permission
    try:
        required_permission = Permissions.GroupPermissions[operationID]  # type: ignore
        if not Permissions.check_permission(Permissions.GroupPermissions(user_permissions),  # type: ignore
                                            required_permission):
            e = Exceptions.GroupExceptions.UserNotAuthorized(account, group, operationID)
            raise HTTPException(e.code, str(e))
    except KeyError:
        e = Exceptions.GroupExceptions.ActionNotFound(operationID)
        raise HTTPException(e.code, str(e))


# Check if the current user has permissions to access the poll and perform requested actions
async def check_poll_permission(request: Request, account: Account = Depends(get_current_active_user)):
    # Extract requested action(operationID) and id of the workspace from the path
    operationID = extract_action_from_path(request)
    pollID = extract_resourceID_from_path(request)
    # Get the poll with the given id
    poll = await Poll.get(ResourceID(pollID), fetch_links=True)
    # Check if poll exists
    e: Exception
    if not poll:
        e = Exceptions.PollExceptions.PollNotFound(pollID)
        raise HTTPException(e.code, str(e))

    # Check if the poll is public
    if poll.public:
        return

    # Get the user policy for the poll
    user_permissions = await Permissions.get_all_permissions(poll, account)

    # Check that the user has the required permission
    try:
        required_permission = Permissions.PollPermissions[operationID]  # type: ignore
        if not Permissions.check_permission(Permissions.PollPermissions(user_permissions),  # type: ignore
                                            required_permission):
            e = Exceptions.PollExceptions.UserNotAuthorized(account, poll, operationID)
            raise HTTPException(e.code, str(e))
    except KeyError:
        e = Exceptions.PollExceptions.ActionNotFound(operationID)
        raise HTTPException(e.code, str(e))
