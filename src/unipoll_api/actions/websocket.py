from typing import Literal
from unipoll_api import dependencies
from . import WorkspaceActions

from unipoll_api.documents import ResourceID


# Workspace actions

async def get_workspaces():
    return await WorkspaceActions.get_workspaces()


async def create_workspace(name: str, description: str = None):
    data = {"name": name, "description": description}
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


async def update_workspace(workspace_id: ResourceID, name: str, description: str = None):
    workspace = await dependencies.get_workspace(workspace_id)
    data = {"name": name, "description": description}
    return await WorkspaceActions.update_workspace(workspace, data)


async def delete_workspace(workspace_id: ResourceID):
    workspace = await dependencies.get_workspace(workspace_id)
    return await WorkspaceActions.delete_workspace(workspace)


# Group actions


async def get_groups(workspace_id: ResourceID):
    workspace = await dependencies.get_workspace(workspace_id)
    return await WorkspaceActions.get_groups(workspace)


async def create_group(workspace_id: ResourceID, name: str, description: str = None):
    workspace = await dependencies.get_workspace(workspace_id)
    data = {"name": name, "description": description}
    return await WorkspaceActions.create_group(workspace, data)


async def get_group(group_id: ResourceID,
                    include: Literal["all"] | list[Literal["members", "policies"]] = []):
    args = {
        "include_members": "members" in include or "all" in include,
        "include_policies": "policies" in include or "all" in include,
    }

    group = await dependencies.get_group(group_id)
    return await WorkspaceActions.get_group(group, **args)
