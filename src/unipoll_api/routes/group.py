# FastAPI
from typing import Annotated, Literal
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from unipoll_api import dependencies as Dependencies
from unipoll_api.actions import GroupActions, PermissionsActions
from unipoll_api.exceptions.resource import APIException
from unipoll_api.schemas import GroupSchemas, PolicySchemas, MemberSchemas
from unipoll_api.documents import Group, ResourceID


# APIRouter creates path operations for user module
open_router: APIRouter = APIRouter()
router: APIRouter = APIRouter(dependencies=[Depends(Dependencies.check_group_permission)])


# Get all groups
# @router.get("/", response_description="Get all groups")
# async def get_all_groups() -> GroupSchemas.GroupList:
#     return await GroupActions.get_all_groups()


query_params = list[Literal["policies", "members", "all"]]


# Get group info by id
@router.get("/{group_id}",
            response_description="Get a group",
            response_model=GroupSchemas.Group,
            response_model_exclude_defaults=True,
            response_model_exclude_none=True)
async def get_group(group: Group = Depends(Dependencies.get_group_model),
                    include: Annotated[query_params | None, Query()] = None):
    try:
        params = {}
        if include:
            if "all" in include:
                params = {"include_members": True, "include_polls": True}
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
                       group: Group = Depends(Dependencies.get_group_model)):
    try:
        return await GroupActions.update_group(group, group_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Delete a group
@router.delete("/{group_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               response_description="Delete a group")
async def delete_group(group: Group = Depends(Dependencies.get_group_model)):
    try:
        await GroupActions.delete_group(group)
        return status.HTTP_204_NO_CONTENT
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get a list of group members
@router.get("/{group_id}/members",
            response_description="List of group members",
            response_model=MemberSchemas.MemberList,
            response_model_exclude_unset=True)
async def get_group_members(group: Group = Depends(Dependencies.get_group_model)):
    try:
        return await GroupActions.get_group_members(group)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Add member to group
@router.post("/{group_id}/members",
             response_description="List of group members",
             response_model=MemberSchemas.MemberList)
async def add_group_members(member_data: MemberSchemas.AddMembers,
                            group: Group = Depends(Dependencies.get_group_model)):
    try:
        return await GroupActions.add_group_members(group, member_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Remove members from the workspace
@router.delete("/{group_id}/members/{account_id}",
               response_description="Updated list removed members",
               response_model_exclude_unset=True)
async def remove_group_member(group: Group = Depends(Dependencies.get_group_model),
                              account_id: ResourceID = Path(..., description="Account ID of the member to remove")):
    try:
        return await GroupActions.remove_group_member(group, account_id)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all policies in the workspace
@router.get("/{group_id}/policies",
            response_description="List of all policies",
            response_model=PolicySchemas.PolicyList,)
async def get_group_policies(group: Group = Depends(Dependencies.get_group_model)) -> PolicySchemas.PolicyList:
    try:
        return await GroupActions.get_group_policies(group)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List user's permissions in the group
@router.get("/{group_id}/policy",
            response_description="List of all member policies",
            response_model=PolicySchemas.PolicyOutput)
async def get_group_policy(group: Group = Depends(Dependencies.get_group_model),
                           account_id: ResourceID | None = None):
    try:
        return await GroupActions.get_group_policy(group, account_id)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Set permissions for a user in a group
@router.put("/{group_id}/policy",
            response_description="Updated policy",
            response_model=PolicySchemas.PolicyOutput)
async def set_group_policy(group: Group = Depends(Dependencies.get_group_model),
                           permissions: PolicySchemas.PolicyInput = Body(...)):
    """
    Sets the permissions for a user in a workspace.
    Query parameters:
        @param workspace_id: id of the workspace to update
    Body parameters:
    - **user_id** (str): id of the user to update
    - **permissions** (int): new permissions for the user
    """
    try:
        return await GroupActions.set_group_policy(group, permissions)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get All Group Permissions
@open_router.get("/permissions",
                 response_description="List of all Group permissions",
                 response_model=PolicySchemas.PermissionList)
async def get_group_permissions():
    try:
        return await PermissionsActions.get_group_permissions()
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))
