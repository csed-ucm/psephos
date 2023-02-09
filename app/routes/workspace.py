# FastAPI
from fastapi import APIRouter, Body, Depends
from app.actions import workspace as WorkspaceActions
from app.actions import group as GroupActions
from app.models.workspace import Workspace
from app.schemas.workspace import (WorkspaceID, WorkspaceList,
                                   WorkspaceCreateInput, WorkspaceCreateOutput)
from app.schemas.group import GroupList, GroupCreateInput, GroupCreateOutput
from app.exceptions import workspace as WorkspaceExceptions


# APIRouter creates path operations for user module
router = APIRouter()


async def get_workspace(workspace_id: WorkspaceID) -> Workspace:
    """
    Returns a workspace with the given id.
    """
    workspace = await Workspace.get(workspace_id)
    if not workspace:
        raise WorkspaceExceptions.WorkspaceNotFound(workspace_id)
    return workspace


# Get all workspaces with user as a member or owner
@router.get("/", response_description="List of all workspaces", response_model=WorkspaceList)
async def get_workspaces() -> WorkspaceList:
    """
    Returns all workspaces, the current user is a member of. The request does not accept any query parameters.
    """
    return await WorkspaceActions.get_all_workspaces()


# Create a new workspace for current user
@router.post("/", response_description="Created workspaces", response_model=WorkspaceCreateOutput)
async def create_workspace(input_data: WorkspaceCreateInput = Body(...)) -> WorkspaceCreateOutput:
    """
    Creates a new workspace for the current user.
    Body parameters:
    - **name** (str): name of the workspace, must be unique
    - **description** (str): description of the workspace

    Returns the created workspace with the current user as the owner.
    """
    return await WorkspaceActions.create_workspace(input_data=input_data)


# List all groups in the workspace
@router.get("/{workspace_id}/groups", response_description="List of all groups", response_model=GroupList)
async def list_groups(workspace: Workspace = Depends(get_workspace)) -> GroupList:
    return await GroupActions.get_all_groups()


# List all groups in the workspace
@router.post("/{workspace_id}/groups", response_description="Created Group", response_model=GroupCreateOutput)
async def create_group(workspace: Workspace = Depends(get_workspace),
                       input_data: GroupCreateInput = Body(...)) -> GroupCreateOutput:
    return await GroupActions.create_group(workspace, input_data)
