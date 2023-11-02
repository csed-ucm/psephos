from typing import Literal
from unipoll_api import dependencies
from . import WorkspaceActions

from unipoll_api.documents import ResourceID


async def get_workspaces():
    return await WorkspaceActions.get_workspaces()


async def create_workspace(name: str, description: str = None):
    data = {"name": name, "description": description}
    return await WorkspaceActions.create_workspace(data)


async def get_workspace(workspace_id: ResourceID, include: Literal["all"] | list = []):
    if include == "all":
        print("include all")
        args = {"include_groups": True, "include_members": True, "include_policies": True, "include_polls": True}
    else:
        args = {"include_groups": "groups" in include,
                "include_members": "members" in include,
                "include_policies": "policies" in include,
                "include_polls": "polls" in include}

    workspace = await dependencies.get_workspace(workspace_id)
    return await WorkspaceActions.get_workspace(workspace, **args)


async def update_workspace(workspace_id: ResourceID, name: str, description: str = None):
    workspace = await dependencies.get_workspace(workspace_id)
    data = {"name": name, "description": description}
    return await WorkspaceActions.update_workspace(workspace, data)


async def delete_workspace(workspace_id: ResourceID):
    workspace = await dependencies.get_workspace(workspace_id)
    return await WorkspaceActions.delete_workspace(workspace)