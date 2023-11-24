
from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from unipoll_api import actions as Actions
from unipoll_api import documents as Documents
from unipoll_api import schemas as Schemas
from unipoll_api import dependencies as Dependencies
from unipoll_api import exceptions as Exceptions

router = APIRouter()


# Get members of a workspace or group
@router.get("", response_description="List of groups", response_model=Schemas.MemberSchemas.MemberList)
async def get_members(workspace: Annotated[Documents.ResourceID | None, Query()] = None,
                      group: Annotated[Documents.ResourceID | None, Query()] = None):
    try:
        if workspace:
            resource = await Dependencies.get_workspace(workspace)
        elif group:
            resource = await Dependencies.get_group(group)
        else:
            raise Exceptions.ResourceExceptions.APIException(422, "Either Workspace or Group must be specified")
        
        return await Actions.MembersActions.get_members(resource=resource)
    except Exceptions.ResourceExceptions.APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Add members to a workspace or group
@router.post("",
             status_code=201,
             response_description="Member list",
             response_model=Schemas.MemberSchemas.MemberList)
async def add_members(input_data: Schemas.MemberSchemas.AddMembersRequest = Body(...)):
    try:
        if input_data.workspace:
            resource = await Dependencies.get_workspace(input_data.workspace)
        elif input_data.group:
            resource = await Dependencies.get_group(input_data.group)
        else:
            raise Exceptions.ResourceExceptions.APIException(422, "Either Workspace or Group must be specified")

        return await Actions.MembersActions.add_members(resource, input_data.accounts)
    except Exceptions.ResourceExceptions.APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


@router.get("/{member_id}",
            response_description="Member Information",
            response_model=Schemas.MemberSchemas.Member)
async def get_member(member = Depends(Dependencies.get_member)):
    try:
        return await Actions.MembersActions.get_member(member)
    except Exceptions.ResourceExceptions.APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))