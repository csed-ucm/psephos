from typing import Literal
from unipoll_api import dependencies
from . import WorkspaceActions, GroupActions, MembersActions
from unipoll_api.schemas import WorkspaceSchemas, GroupSchemas, MemberSchemas
from unipoll_api.documents import ResourceID
from unipoll_api.exceptions.resource import APIException


# Workspace actions


async def get_workspaces():
    return await WorkspaceActions.get_workspaces()


async def create_workspace(name: str, description: str = ""):
    data = WorkspaceSchemas.WorkspaceCreateInput(name=name, description=description)
    return await WorkspaceActions.create_workspace(data)


async def get_workspace(workspace_id: ResourceID,
                        include: Literal["all"] | list[Literal["groups", "members", "policies", "polls"]] = []):
    args = {
        "include_groups": "groups" in include or "all" in include,
        "include_members": "members" in include or "all" in include,
        "include_policies": "policies" in include or "all" in include,
        "include_polls": "polls" in include or "all" in include,
    }

    workspace = await dependencies.get_workspace(workspace_id)
    return await WorkspaceActions.get_workspace(workspace, **args)


async def update_workspace(workspace_id: ResourceID, name: str, description: str = ""):
    workspace = await dependencies.get_workspace(workspace_id)
    data = WorkspaceSchemas.WorkspaceUpdateRequest(name=name, description=description)
    return await WorkspaceActions.update_workspace(workspace, data)


async def delete_workspace(workspace_id: ResourceID):
    workspace = await dependencies.get_workspace(workspace_id)
    return await WorkspaceActions.delete_workspace(workspace)


# Group actions


async def get_groups(workspace_id: ResourceID):
    workspace = await dependencies.get_workspace(workspace_id)
    return await GroupActions.get_groups(workspace)


async def create_group(workspace_id: ResourceID, name: str, description: str = ""):
    workspace = await dependencies.get_workspace(workspace_id)
    # data = GroupSchemas.GroupCreateInput(name=name, description=description)
    return await GroupActions.create_group(workspace, name, description)


async def get_group(group_id: ResourceID,
                    include: Literal["all"] | list[Literal["members", "policies"]] = []):
    args = {
        "include_members": "members" in include or "all" in include,
        "include_policies": "policies" in include or "all" in include,
    }

    group = await dependencies.get_group(group_id)
    return await GroupActions.get_group(group, **args)


async def update_group(group_id: ResourceID, name: str, description: str = ""):
    group = await dependencies.get_group(group_id)
    data = GroupSchemas.GroupUpdateRequest(name=name, description=description)
    return await GroupActions.update_group(group, data)


async def delete_group(group_id: ResourceID):
    group = await dependencies.get_group(group_id)
    return await GroupActions.delete_group(group)


# Member actions


async def get_members(workspace_id: ResourceID | None = None,
                      group_id: ResourceID | None = None):
    if workspace_id and group_id:
        raise ValueError("workspace_id and group_id can't be both provided")

    if workspace_id:
        resource = await dependencies.get_workspace(workspace_id)
    elif group_id:
        resource = await dependencies.get_group(group_id)
    else:
        raise APIException(422, "workspace_id or group_id must be provided")

    return await MembersActions.get_members(resource)


async def add_members(workspace_id: ResourceID | None = None,
                      group_id: ResourceID | None = None,
                      account_id_list: list[ResourceID] = []):
    # data = MemberSchemas.AddMembersRequest(accounts=account_id_list, workspace=workspace_id, group=group_id)

    if workspace_id:
        resource = await dependencies.get_workspace(workspace_id)
    elif group_id:
        resource = await dependencies.get_group(group_id)
    else:
        raise APIException(422, "workspace_id or group_id must be provided")

    return await MembersActions.add_members(resource, account_id_list)
