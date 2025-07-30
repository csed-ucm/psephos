# FastAPI
from typing import Annotated, Literal
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from unipoll_api import dependencies as Dependencies
from unipoll_api import actions, AccountManager
from unipoll_api.exceptions.resource import APIException
from unipoll_api.documents import Poll, Workspace
from unipoll_api.schemas import PollSchemas, PolicySchemas
from unipoll_api.utils import Permissions


router: APIRouter = APIRouter()


# Get Workspace Polls
@router.get("/workspaces/{workspace_id}/polls",
            tags=["Polls"],
            response_description="List of all polls in the workspace",
            response_model=PollSchemas.PollList,
            response_model_exclude_none=True)
async def get_polls(workspace: Workspace = Depends(Dependencies.get_workspace)):
    try:
        return await actions.PollActions.get_polls(workspace)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Create a new poll in the workspace
@router.post("/workspaces/{workspace_id}/polls",
             tags=["Polls"],
             response_description="Created poll",
             status_code=201,
             response_model=PollSchemas.PollResponse)
async def create_poll(workspace: Workspace = Depends(Dependencies.get_workspace),
                      input_data: PollSchemas.CreatePollRequest = Body(...)):
    try:
        return await actions.PollActions.create_poll(workspace, input_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get a poll in the workspace
@router.get("/workspaces/{workspace_id}/polls/{poll_id}",
            tags=["Polls"],
            response_description="Poll data",
            response_model=PollSchemas.PollResponse)
async def get_poll(workspace: Workspace = Depends(Dependencies.get_workspace),
                   poll: Poll = Depends(Dependencies.get_poll),
                   include: Annotated[list[Literal["all", "policies", "questions"]] | None, Query()] = None):
    try:
        params = {}
        if include:
            if "all" in include:
                params = {"include_questions": True,
                          "include_policies": True}
            else:
                if "groups" in include:
                    params["include_questions"] = True
                if "policies" in include:
                    params["include_policies"] = True
        return await actions.PollActions.get_poll(poll, **params)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Update a poll in the workspace
@router.patch("/workspaces/{workspace_id}/polls/{poll_id}",
              tags=["Polls"],
              response_description="Updated poll",
              response_model=PollSchemas.PollResponse)
async def update_poll(poll: Poll = Depends(Dependencies.get_poll),
                      input_data: PollSchemas.UpdatePollRequest = Body(...)):
    try:
        return await actions.PollActions.update_poll(poll, input_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Delete a poll in the workspace
@router.delete("/workspaces/{workspace_id}/polls/{poll_id}",
               tags=["Polls"],
               response_description="Deleted poll",
               status_code=204)
async def delete_poll(poll: Poll = Depends(Dependencies.get_poll)):
    try:
        await actions.PollActions.delete_poll(poll)
        return status.HTTP_204_NO_CONTENT
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


#TODO: Add poll policies endpoints


# Get All Member Permissions in the Group
@router.get("/workspaces/{workspace_id}/polls/{poll_id}/permissions",
            tags=["Poll Permissions"],
            response_description="List of all member permissions in the workspace",
            response_model=PolicySchemas.PermissionList)
async def get_poll_member_permissions(poll: Poll = Depends(Dependencies.get_poll)):
    try:
        #TODO: Create an Action for this
        account = AccountManager.active_user.get()
        member = await Dependencies.get_member_by_account(account, poll.workspace)  # type: ignore
        poll_permissions = await Permissions.get_all_permissions(poll, member)
        return PolicySchemas.PermissionList(permissions=Permissions.convert_permission_to_string(poll_permissions, "Poll"))
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))