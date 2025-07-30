# FastAPI
from typing import Annotated, Literal
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from unipoll_api import dependencies as Dependencies
from unipoll_api.actions import GroupActions, PermissionsActions, MembersActions, PolicyActions
from unipoll_api.exceptions.resource import APIException
from unipoll_api.schemas import GroupSchemas, PolicySchemas, MemberSchemas
from unipoll_api.documents import Account, Group, Policy, ResourceID


router: APIRouter = APIRouter()


# Get groups
@router.get("/", response_description="List of groups")
async def get_all_groups(workspace: Annotated[ResourceID | None, Query()] = None,
                         account: Annotated[ResourceID | None, Query()] = None,
                         name: Annotated[str | None, Query()] = None
                         ) -> GroupSchemas.GroupList:
    return await GroupActions.get_groups(workspace=await Dependencies.get_workspace(workspace) if workspace else None,
                                         account=await Dependencies.get_account(account) if account else None,
                                         name=name)


# Create a new group
@router.post("/",
             status_code=201,
             response_description="Created Group",
             response_model=GroupSchemas.GroupCreateOutput)
async def create_group(input_data: GroupSchemas.GroupCreateRequest = Body(...)):
    try:
        workspace = await Dependencies.get_workspace(input_data.workspace)
        return await GroupActions.create_group(workspace, name=input_data.name, description=input_data.description)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


query_params = list[Literal["policies", "members", "all"]]


# Get group info by id
@router.get("/{group_id}",
            response_description="Get a group",
            response_model=GroupSchemas.Group,
            response_model_exclude_defaults=True,
            response_model_exclude_none=True)
async def get_group(group: Group = Depends(Dependencies.get_group),
                    include: Annotated[query_params | None, Query()] = None):
    try:
        params = {}
        if include:
            if "all" in include:
                params = {"include_members": True, "include_policies": True}
            else:
                if "members" in include:
                    params["include_members"] = True
                if "policies" in include:
                    params["include_policies"] = True
        return await GroupActions.get_group(group, **params)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Update group info
@router.patch("/{group_id}",
              response_description="Update a group",
              response_model=GroupSchemas.GroupShort)
async def update_group(group_data: GroupSchemas.GroupUpdateRequest,
                       group: Group = Depends(Dependencies.get_group)):
    try:
        return await GroupActions.update_group(group, group_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Delete a group
@router.delete("/{group_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               response_description="Delete a group")
async def delete_group(group: Group = Depends(Dependencies.get_group)):
    try:
        await GroupActions.delete_group(group)
        return status.HTTP_204_NO_CONTENT
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))
