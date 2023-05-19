# FastAPI
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from app.actions import workspace as WorkspaceActions
from app.exceptions.resource import APIException
from app.models.documents import Workspace, ResourceID
from app.schemas import workspace as WorkspaceSchemas
from app.schemas import policy as PolicySchemas
from app.schemas import group as GroupSchemas
from app.schemas import member as MemberSchemas
from app import dependencies as Dependencies


# Dependency for getting a workspace with the given id with http exception
# async def check_workspace_permission(request: Request, account: Account = Depends(get_current_active_user)):
#     try:
#         await Dependencies.check_workspace_permission(request, account)
#     except APIException as e:
#         raise HTTPException(status_code=e.code, detail=str(e))


# APIRouter creates path operations for user module
open_router = APIRouter()
router = APIRouter(dependencies=[Depends(Dependencies.check_workspace_permission)])


# TODO: Move to open router to a separate file
# Get all workspaces with user as a member or owner
@open_router.get("",
                 response_description="List of all workspaces",
                 response_model=WorkspaceSchemas.WorkspaceList)
async def get_workspaces():
    """
    Returns all workspaces where the current user is a member.
    The request does not accept any query parameters.
    """
    try:
        return await WorkspaceActions.get_workspaces()
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Create a new workspace for current user
@open_router.post("",
                  response_description="Created workspaces",
                  status_code=201,
                  response_model=WorkspaceSchemas.WorkspaceCreateOutput)
async def create_workspace(input_data: WorkspaceSchemas.WorkspaceCreateInput = Body(...)):
    """
    Creates a new workspace for the current user.
    Body parameters:
    - **name** (str): name of the workspace, must be unique
    - **description** (str): description of the workspace

    Returns the created workspace information.
    """
    try:
        return await WorkspaceActions.create_workspace(input_data=input_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get a workspace with the given id
@router.get("/{workspace_id}", response_description="Workspace data")
async def get_workspace(workspace: Workspace = Depends(Dependencies.get_workspace_model)):
    """
    Returns a workspace with the given id.
    """
    try:
        return await WorkspaceActions.get_workspace(workspace)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Update a workspace with the given id
@router.patch("/{workspace_id}", response_description="Updated workspace")
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
    try:
        return await WorkspaceActions.update_workspace(workspace, input_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Delete a workspace with the given id
@router.delete("/{workspace_id}",
               response_description="Deleted workspace",
               status_code=204)
async def delete_workspace(workspace: Workspace = Depends(Dependencies.get_workspace_model)):
    """
    Deletes the workspace with the given id.
    Query parameters:
        @param workspace_id: id of the workspace to delete

    Returns status code 204 if the workspace is deleted successfully.
    Response has no detail.
    """
    try:
        await WorkspaceActions.delete_workspace(workspace)
        return status.HTTP_204_NO_CONTENT
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all groups in the workspace
@router.get("/{workspace_id}/groups",
            response_description="List of all groups",
            response_model=GroupSchemas.GroupList)
async def get_groups(workspace: Workspace = Depends(Dependencies.get_workspace_model)):
    try:
        return await WorkspaceActions.get_groups(workspace)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all groups in the workspace
@router.post("/{workspace_id}/groups",
             response_description="Created Group",
             response_model=GroupSchemas.GroupCreateOutput)
async def create_group(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                       input_data: GroupSchemas.GroupCreateInput = Body(...)):
    try:
        return await WorkspaceActions.create_group(workspace, input_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all members in the workspace
@router.get("/{workspace_id}/members",
            response_description="List of all groups",
            response_model=MemberSchemas.MemberList,
            response_model_exclude_unset=True)
async def get_workspace_members(workspace: Workspace = Depends(Dependencies.get_workspace_model)):
    try:
        return await WorkspaceActions.get_workspace_members(workspace)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Add members to the workspace
@router.post("/{workspace_id}/members",
             response_description="List added members",
             response_model=MemberSchemas.MemberList)
async def add_workspace_members(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                                member_data: MemberSchemas.AddMembers = Body(...)):
    try:
        return await WorkspaceActions.add_workspace_members(workspace, member_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Remove members from the workspace
@router.delete("/{workspace_id}/members/{account_id}",
               response_description="List removed members",
               response_model_exclude_unset=True)
async def remove_workspace_member(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                                  account_id: ResourceID = Path(..., description="Account ID of the member to remove")):
    try:
        return await WorkspaceActions.remove_workspace_member(workspace, account_id)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all policies in the workspace
@router.get("/{workspace_id}/all_policies",
            response_description="List of all policies",
            response_model=PolicySchemas.PolicyList)
async def get_all_workspace_policies(workspace: Workspace = Depends(Dependencies.get_workspace_model)):
    try:
        return await WorkspaceActions.get_all_workspace_policies(workspace)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List user's permissions in the workspace
@router.get("/{workspace_id}/policy",
            response_description="List user policy(permissions)",
            response_model=PolicySchemas.PolicyOutput)
async def get_workspace_policy(workspace: Workspace = Depends(Dependencies.get_workspace_model),
                               account_id: ResourceID | None = None):
    try:
        return await WorkspaceActions.get_workspace_policy(workspace, account_id)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Set permissions for a user in a workspace
@router.put("/{workspace_id}/policy",
            response_description="Updated permissions",
            response_model=PolicySchemas.PolicyOutput)
async def set_workspace_policy(workspace: Workspace = Depends(Dependencies.get_workspace_model),
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
    try:
        return await WorkspaceActions.set_workspace_policy(workspace, permissions)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))
