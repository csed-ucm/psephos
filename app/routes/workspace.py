# FastAPI
from fastapi import APIRouter
from app.schemas.workspace import (WorkspaceList)
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
