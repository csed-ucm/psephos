# FastAPI
from typing import Annotated, Literal
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from unipoll_api import dependencies as Dependencies
from unipoll_api import actions
from unipoll_api.exceptions.resource import APIException
from unipoll_api.documents import Account, Workspace, ResourceID, Policy
from unipoll_api.schemas import WorkspaceSchemas, PolicySchemas, GroupSchemas, MemberSchemas, PollSchemas

# APIRouter creates path operations for user module
open_router: APIRouter = APIRouter()
# router: APIRouter = APIRouter(dependencies=[Depends(Dependencies.check_workspace_permission)])
router: APIRouter = APIRouter()


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
        return await actions.WorkspaceActions.get_workspaces()
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
        return await actions.WorkspaceActions.create_workspace(input_data=input_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


query_params = list[Literal["all", "policies", "groups", "members", "polls"]]


# Get a workspace with the given id
@router.get("/{workspace_id}",
            response_description="Workspace data",
            response_model=WorkspaceSchemas.Workspace,
            response_model_exclude_defaults=True,
            response_model_exclude_none=True)
async def get_workspace(workspace: Workspace = Depends(Dependencies.get_workspace),
                        include: Annotated[query_params | None, Query()] = None):
    """
    ### Description:
    Endpoint to get a workspace with the given id.
    By default, it returns the basic information of the workspace such as id, name, and description.
    The user can specify other resources to include in the response using the query parameters.

    For example, to include groups and members in the response, the user can send the following GET request:
    > `/workspaces/6497fdbafe12e8ff9017f253?include=groups&include=members`

    To include all resources, the user can send the following GET request:
    > `/workspaces/6497fdbafe12e8ff9017f253?include=all`

    To get basic information of the workspace, the user can send the following GET request:
    > `/workspaces/6497fdbafe12e8ff9017f253`

    ### Path parameters:
    - **workspace_id** (str): id of the workspace

    ### Query parameters:
    - **include** (str): resources to include in the response

        #### Possible values:
        - **groups**: include groups in the response
        - **members**: include members in the response
        - **policies**: include policies in the response
        - **all**: include all resources in the response

    ### Response:
    Returns a workspace with the given id.
    """
    try:
        params = {}
        if include:
            if "all" in include:
                params = {"include_groups": True,
                          "include_members": True,
                          "include_policies": True,
                          "include_polls": True}
            else:
                if "groups" in include:
                    params["include_groups"] = True
                if "members" in include:
                    params["include_members"] = True
                if "policies" in include:
                    params["include_policies"] = True
                if "polls" in include:
                    params["include_polls"] = True
        return await actions.WorkspaceActions.get_workspace(workspace, **params)

    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Update a workspace with the given id
@router.patch("/{workspace_id}",
              response_description="Updated workspace",
              response_model=WorkspaceSchemas.Workspace,
              response_model_exclude_none=True)
async def update_workspace(workspace: Workspace = Depends(Dependencies.get_workspace),
                           input_data: WorkspaceSchemas.WorkspaceUpdateRequest = Body(...)):
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
        return await actions.WorkspaceActions.update_workspace(workspace, input_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Delete a workspace with the given id
@router.delete("/{workspace_id}",
               response_description="Deleted workspace",
               status_code=204)
async def delete_workspace(workspace: Workspace = Depends(Dependencies.get_workspace)):
    """
    Deletes the workspace with the given id.
    Query parameters:
        @param workspace_id: id of the workspace to delete

    Returns status code 204 if the workspace is deleted successfully.
    Response has no detail.
    """
    try:
        await actions.WorkspaceActions.delete_workspace(workspace)
        return status.HTTP_204_NO_CONTENT
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all groups in the workspace
@router.get("/{workspace_id}/groups",
            response_description="List of all groups",
            response_model=GroupSchemas.GroupList)
async def get_groups(workspace: Workspace = Depends(Dependencies.get_workspace)):
    try:
        return await actions.GroupActions.get_groups(workspace)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all groups in the workspace
@router.post("/{workspace_id}/groups",
             status_code=201,
             response_description="Created Group",
             response_model=GroupSchemas.GroupCreateOutput)
async def create_group(workspace: Workspace = Depends(Dependencies.get_workspace),
                       input_data: GroupSchemas.GroupCreateInput = Body(...)):
    try:
        return await actions.GroupActions.create_group(workspace, input_data.name, input_data.description)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all members in the workspace
@router.get("/{workspace_id}/members",
            response_description="List of all groups",
            response_model=MemberSchemas.MemberList,
            response_model_exclude_unset=True)
async def get_workspace_members(workspace: Workspace = Depends(Dependencies.get_workspace)):
    try:
        return await actions.MembersActions.get_members(workspace)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Add members to the workspace
@router.post("/{workspace_id}/members",
             response_description="List added members",
             response_model=MemberSchemas.MemberList)
async def add_workspace_members(workspace: Workspace = Depends(Dependencies.get_workspace),
                                member_data: MemberSchemas.AddMembers = Body(...)):
    try:
        return await actions.MembersActions.add_members(workspace, member_data.accounts)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Remove member from the workspace
@router.delete("/{workspace_id}/members/{account_id}",
               response_description="Updated list removed members",
               response_model_exclude_unset=True)
async def remove_workspace_member(workspace: Workspace = Depends(Dependencies.get_workspace),
                                  account: Account = Depends(Dependencies.get_account)):
    try:
        return await actions.MembersActions.remove_member(workspace, account)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all policies in the workspace
@router.get("/{workspace_id}/policies",
            response_description="List of all policies",
            response_model=PolicySchemas.PolicyList)
async def get_workspace_policies(workspace: Workspace = Depends(Dependencies.get_workspace),
                                 account_id: ResourceID = Query(None)):
    try:
        account = await Dependencies.get_account(account_id) if account_id else None
        member = await Dependencies.get_member(account, workspace) if account else None
        return await actions.PolicyActions.get_policies(resource=workspace, policy_holder=member)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Set permissions for a member in a workspace
@router.put("/{workspace_id}/policies/{policy_id}",
            response_description="Updated permissions",
            response_model=PolicySchemas.PolicyOutput)
async def set_workspace_policy(workspace: Workspace = Depends(Dependencies.get_workspace),
                               policy: Policy = Depends(Dependencies.get_policy),
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
        return await actions.PolicyActions.update_policy(policy, new_permissions=permissions.permissions)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get All Workspace Permissions
@open_router.get("/permissions",
                 response_description="List of all workspace permissions",
                 response_model=PolicySchemas.PermissionList)
async def get_workspace_permissions():
    try:
        return await actions.PermissionsActions.get_workspace_permissions()
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get Workspace Polls
@router.get("/{workspace_id}/polls",
            response_description="List of all polls in the workspace",
            response_model=PollSchemas.PollList,
            response_model_exclude_none=True)
async def get_polls(workspace: Workspace = Depends(Dependencies.get_workspace)):
    try:
        return await actions.PollActions.get_polls(workspace)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Create a new poll in the workspace
@router.post("/{workspace_id}/polls",
             response_description="Created poll",
             status_code=201,
             response_model=PollSchemas.PollResponse)
async def create_poll(workspace: Workspace = Depends(Dependencies.get_workspace),
                      input_data: PollSchemas.CreatePollRequest = Body(...)):
    try:
        return await actions.PollActions.create_poll(workspace, input_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))
