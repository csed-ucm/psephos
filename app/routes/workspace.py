# FastAPI
from fastapi import APIRouter, Body, Depends
from app.actions import workspace as WorkspaceActions
from app.models.documents import Workspace, Account, ResourceID
from app.schemas import workspace as WorkspaceSchemas
from app.schemas import policy as PolicySchemas
# from app.schemas.user import UserID
from app.schemas.group import GroupList, GroupCreateInput, GroupCreateOutput
from app import dependencies as Dependencies
from app.account_manager import get_current_active_user

# APIRouter creates path operations for user module
open_router = APIRouter()
router = APIRouter(dependencies=[Depends(Dependencies.check_workspace_permission)])


# TODO: Move to open router to a separate file
# Get all workspaces with user as a member or owner
@open_router.get("", response_description="List of all workspaces", response_model=WorkspaceSchemas.WorkspaceList)
async def get_workspaces() -> WorkspaceSchemas.WorkspaceList:
    """
    Returns all workspaces where the current user is a member.
    The request does not accept any query parameters.
    """
    return await WorkspaceActions.get_workspaces()


# Create a new workspace for current user
@open_router.post("", response_description="Created workspaces",
                  response_model=WorkspaceSchemas.WorkspaceCreateOutput)
async def create_workspace(input_data: WorkspaceSchemas.WorkspaceCreateInput = Body(...)) -> WorkspaceSchemas.WorkspaceCreateOutput:
    """
    Creates a new workspace for the current user.
    Body parameters:
    - **name** (str): name of the workspace, must be unique
    - **description** (str): description of the workspace

    Returns the created workspace information.
    """
    return await WorkspaceActions.create_workspace(input_data=input_data)


# Get a workspace with the given id
@router.get("/{workspace_id}", response_description="Workspace data")
async def get_workspace(workspace: Workspace = Depends(Dependencies.get_workspace_model)):
    """
    Returns a workspace with the given id.
    """
    return await WorkspaceActions.get_workspace(workspace)


# Update a workspace with the given id
@router.put("/{workspace_id}", response_description="Updated workspace")
async def update_workspace(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                           input_data: WorkspaceSchemas.WorkspaceCreateInput = Body(...)):
    """
    Updates the workspace with the given id.
    Query parameters:
        @param workspace_id: id of the workspace to update
    Body parameters:
    - **name** (str): name of the workspace, must be unique
    - **description** (str): description of the workspace

    Returns the updated workspace.
    """
    return await WorkspaceActions.update_workspace(workspace, input_data)


# Delete a workspace with the given id
@router.delete("/{workspace_id}", response_description="Deleted workspace")
async def delete_workspace(workspace: Workspace = Depends(Dependencies.get_workspace_model)):
    """
    Deletes the workspace with the given id.
    Query parameters:
        @param workspace_id: id of the workspace to delete
    """
    return await WorkspaceActions.delete_workspace(workspace)


# List all groups in the workspace
@router.get("/{workspace_id}/groups", response_description="List of all groups", response_model=GroupList)
async def get_groups(workspace: Workspace = Depends(Dependencies.get_workspace_model)) -> GroupList:
    return await WorkspaceActions.get_groups(workspace)


# List all groups in the workspace
@router.post("/{workspace_id}/groups", response_description="Created Group", response_model=GroupCreateOutput)
async def create_group(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                       input_data: GroupCreateInput = Body(...)) -> GroupCreateOutput:
    return await WorkspaceActions.create_group(workspace, input_data)


# List all members in the workspace
@router.get("/{workspace_id}/members", response_description="List of all groups", response_model=dict)
async def get_workspace_members(workspace: Workspace = Depends(Dependencies.get_workspace_model)) -> dict:
    return await WorkspaceActions.get_workspace_members(workspace)


# List all members in the workspace
@router.post("/{workspace_id}/members", response_description="List of all groups", response_model=Account)
async def add_workspace_members(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                      member_data: WorkspaceSchemas.MemberAdd = Body(...)):
    return await WorkspaceActions.add_workspace_members(workspace, member_data.user_id)


# List user's permissions in the workspace
@router.get("/{workspace_id}/permissions", response_description="List of all groups")
async def get_workspace_permissions(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                                    account_id: ResourceID | None = None):
    return await WorkspaceActions.get_workspace_permissions(workspace, account_id)


# Set permissions for a user in a workspace
@router.put("/{workspace_id}/permissions", response_description="Updated permissions")
async def set_workspace_permissions(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                          permissions: PolicySchemas.PolicyInput = Body(...)):
    """
    Sets the permissions for a user in a workspace.
    Query parameters:
        @param workspace_id: id of the workspace to update
    Body parameters:
    - **user_id** (str): id of the user to update
    - **permissions** (int): new permissions for the user

    Returns the updated workspace.
    """
    return await WorkspaceActions.set_workspace_permissions(workspace, permissions)
