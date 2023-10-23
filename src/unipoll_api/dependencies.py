from typing import Annotated
from functools import wraps
# from bson import DBRef
from fastapi import Cookie, Depends, Query, HTTPException, WebSocket
from unipoll_api.account_manager import active_user, get_current_active_user
from unipoll_api.documents import ResourceID, Workspace, Group, Account, Poll, Policy, Member
from unipoll_api import exceptions as Exceptions


# Wrapper to handle exceptions and raise HTTPException
def http_dependency(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exceptions.ResourceExceptions.APIException as e:
            raise HTTPException(status_code=e.code, detail=str(e))
    return wrapper


# Dependency to get account by id
@http_dependency
async def get_account(account_id: ResourceID) -> Account:
    """
    Returns an account with the given id.
    """
    account = await Account.get(account_id)
    if not account:
        raise Exceptions.AccountExceptions.AccountNotFound(account_id)
    return account


async def get_member(account: Account, resource: Workspace | Group) -> Member:
    """
    Returns a member with the given id.
    """

    for member in resource.members:
        if member.account.id == account.id:  # type: ignore
            return member  # type: ignore
    raise Exceptions.ResourceExceptions.ResourceNotFound("member", account.id)


async def websocket_auth(websocket: WebSocket,
                         session: Annotated[str | None, Cookie()] = None,
                         token: Annotated[str | None, Query()] = None) -> dict:
    return {"cookie": session, "token": token}


# Dependency for getting a workspace with the given id
@http_dependency
async def get_workspace(workspace_id: ResourceID) -> Workspace:
    """
    Returns a workspace with the given id.
    """
    workspace = await Workspace.get(workspace_id, fetch_links=True)

    if workspace:
        return workspace
    raise Exceptions.WorkspaceExceptions.WorkspaceNotFound(workspace_id)


# Dependency to get a group by id and verify it exists
@http_dependency
async def get_group(group_id: ResourceID) -> Group:
    """
    Returns a group with the given id.
    """
    group = await Group.get(group_id, fetch_links=True)
    if group:
        return group
    raise Exceptions.GroupExceptions.GroupNotFound(group_id)


# Dependency to get a poll by id and verify it exists
@http_dependency
async def get_poll(poll_id: ResourceID) -> Poll:
    """
    Returns a poll with the given id.
    """
    poll = await Poll.get(poll_id, fetch_links=True)
    if poll:
        return poll
    raise Exceptions.GroupExceptions.GroupNotFound(poll_id)


# Dependency to get a policy by id and verify it exists
@http_dependency
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
