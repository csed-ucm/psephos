# FastAPI
from fastapi import APIRouter, Body, Depends, HTTPException, status
from app import dependencies as Dependencies
from app.actions import group as GroupActions
from app.exceptions.resource import APIException
from app.schemas import group as GroupSchemas
from app.schemas import policy as PolicySchemas
from app.schemas import member as MemberSchemas
from app.models.documents import Group, ResourceID


# APIRouter creates path operations for user module
open_router = APIRouter()
router = APIRouter(dependencies=[Depends(Dependencies.check_group_permission)])


# Get all groups
# @router.get("/", response_description="Get all groups")
# async def get_all_groups() -> GroupSchemas.GroupList:
#     return await GroupActions.get_all_groups()


# Get group info by id
@router.get("/{group_id}",
            response_description="Get a group",
            response_model=GroupSchemas.GroupShort)
async def get_group(group: Group = Depends(Dependencies.get_group_model)):
    try:
        return await GroupActions.get_group(group)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Update group info
@router.patch("/{group_id}",
              response_description="Update a group",
              response_model=GroupSchemas.GroupShort)
async def update_group(group_data: GroupSchemas.GroupUpdateIn,
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
            response_description="Get a list of group members",
            response_model=MemberSchemas.MemberList)
async def get_group_members(group: Group = Depends(Dependencies.get_group_model)):
    try:
        return await GroupActions.get_group_members(group)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Add member to group
@router.post("/{group_id}/members",
             response_description="Get a group",
             response_model=MemberSchemas.MemberList)
async def add_group_members(member_data: MemberSchemas.AddMembers,
                            group: Group = Depends(Dependencies.get_group_model)):
    try:
        await GroupActions.add_group_members(group, member_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List user's permissions in the group
@router.get("/{group_id}/permissions", response_description="List of all groups")
async def get_group_permissions(group: Group = Depends(Dependencies.get_group_model),
                                account_id: ResourceID | None = None):
    try:
        await GroupActions.get_group_permissions(group, account_id)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Set permissions for a user in a workspace
@router.put("/{group_id}/permissions", response_description="Updated permissions")
async def set_group_permissions(group: Group = Depends(Dependencies.get_group_model),
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
        await GroupActions.set_group_permissions(group, permissions)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))
