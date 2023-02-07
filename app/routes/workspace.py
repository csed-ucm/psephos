# FastAPI
from fastapi import APIRouter, Body
from app.schemas.workspace import (WorkspaceList,
                                   WorkspaceCreateInput, WorkspaceCreateOutput)
from app.actions import workspace as WorkspaceActions


# APIRouter creates path operations for user module
router = APIRouter()


# Get all workspaces with user as a member or owner
@router.get("/", response_description="List of all groups", response_model=WorkspaceList)
async def get_workspaces() -> WorkspaceList:
    """
    Returns all workspaces, the current user is a member of. The request does not accept any query parameters.
    """
    return await WorkspaceActions.get_user_workspaces()


# Create a new workspace for current user
@router.post("/", response_description="Created group", response_model=WorkspaceCreateOutput)
async def create_group(input_data: WorkspaceCreateInput = Body(...)) -> WorkspaceCreateOutput:
    """
    Creates a new workspace for the current user.
    Body parameters:
    - **name** (str): name of the workspace, must be unique
    - **description** (str): description of the workspace

    Returns the created workspace with the current user as the owner.
    """
    return await WorkspaceActions.create_workspace(input_data=input_data)
