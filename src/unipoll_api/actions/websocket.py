from typing import Literal
from unipoll_api import dependencies
from . import WorkspaceActions, GroupActions, MembersActions, PolicyActions
from unipoll_api.schemas import WorkspaceSchemas, GroupSchemas, MemberSchemas
from unipoll_api.documents import ResourceID
from unipoll_api.exceptions.resource import APIException


# Workspace actions


async def get_workspaces():
    return await WorkspaceActions.get_workspaces()


async def create_workspace(name: str, description: str = ""):
    data = WorkspaceSchemas.WorkspaceCreateInput(name=name, description=description)
    return await WorkspaceActions.create_workspace(data)


async def get_workspace_info(workspace_id: ResourceID):
    workspace = await dependencies.get_workspace(workspace_id)
    return await WorkspaceActions.get_workspace(workspace, **args)


async def update_workspace_info(workspace_id: ResourceID, name: str, description: str = ""):
    workspace = await dependencies.get_workspace(workspace_id)
    data = WorkspaceSchemas.WorkspaceUpdateRequest(name=name, description=description)
    return await WorkspaceActions.update_workspace(workspace, data)


async def delete_workspace(workspace_id: ResourceID):
    workspace = await dependencies.get_workspace(workspace_id)
    return await WorkspaceActions.delete_workspace(workspace)


async def get_workspace_members(workspace_id: ResourceID):
    workspace = await dependencies.get_workspace(workspace_id)
    return await MembersActions.get_members(workspace)


async def add_workspace_members(workspace_id: ResourceID, account_id_list: list[ResourceID]):
    workspace = await dependencies.get_workspace(workspace_id)
    return await MembersActions.add_members(workspace, account_id_list)


async def get_workspace_policies(workspace_id: ResourceID):
    workspace = await dependencies.get_workspace(workspace_id)
    return await PolicyActions.get_policies(resource=workspace)


# Group actions


async def get_groups(workspace_id: ResourceID):
    workspace = await dependencies.get_workspace(workspace_id)
    return await GroupActions.get_groups(workspace)


async def create_group(workspace_id: ResourceID, name: str, description: str = ""):
    workspace = await dependencies.get_workspace(workspace_id)
    # data = GroupSchemas.GroupCreateInput(name=name, description=description)
    return await GroupActions.create_group(workspace, name, description)


async def get_group_info(group_id: ResourceID):
    group = await dependencies.get_group(group_id)
    return await GroupActions.get_group(group)


async def update_group_info(group_id: ResourceID, name: str, description: str = ""):
    group = await dependencies.get_group(group_id)
    data = GroupSchemas.GroupUpdateRequest(name=name, description=description)
    return await GroupActions.update_group(group, data)


async def delete_group(group_id: ResourceID):
    group = await dependencies.get_group(group_id)
    return await GroupActions.delete_group(group)


async def get_group_members(group_id: ResourceID):
    group = await dependencies.get_group(group_id)
    return await MembersActions.get_members(group)


async def add_group_members(group_id: ResourceID, account_id_list: list[ResourceID]):
    group = await dependencies.get_group(group_id)
    return await MembersActions.add_members(group, account_id_list)


async def get_group_policies(group_id: ResourceID):
    group = await dependencies.get_group(group_id)
    return await PolicyActions.get_policies(resource=group)