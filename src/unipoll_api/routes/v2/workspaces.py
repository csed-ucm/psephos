# FastAPI
from typing import Annotated, Literal
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from unipoll_api import dependencies as Dependencies
from unipoll_api.actions.__interface__ import WorkspaceActions
from unipoll_api.exceptions.resource import APIException
from unipoll_api.documents import Account, Workspace, ResourceID, Policy
from unipoll_api.schemas import WorkspaceSchemas, PolicySchemas, GroupSchemas, MemberSchemas, PollSchemas


router: APIRouter = APIRouter()


# Get all workspaces with user as a member or owner
@router.get("",
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
@router.post("",
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
        return await WorkspaceActions.get_workspace(workspace, **params)

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
        return await WorkspaceActions.update_workspace(workspace, input_data)
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
        await WorkspaceActions.delete_workspace(workspace)
        return status.HTTP_204_NO_CONTENT
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))
