# FastAPI
from typing import Annotated, Literal
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi_versioning import version
from unipoll_api import dependencies as Dependencies
from unipoll_api.actions import GroupActions, PermissionsActions, MembersActions, PolicyActions
from unipoll_api.exceptions.resource import APIException
from unipoll_api.schemas import GroupSchemas, PolicySchemas, MemberSchemas
from unipoll_api.documents import Account, Group, Policy, ResourceID, Member

router = APIRouter()

query_params = list[Literal["policies", "members", "all"]]


# Get group info by id

@router.get("/{group_id}",
            tags=["Groups"],
            response_description="Get a group",
            response_model=GroupSchemas.Group,
            response_model_exclude_defaults=True,
            response_model_exclude_none=True)
@version(1)
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
              tags=["Groups"],
              response_description="Update a group",
              response_model=GroupSchemas.GroupShort)
@version(1)
async def update_group(group_data: GroupSchemas.GroupUpdateRequest,
                       group: Group = Depends(Dependencies.get_group)):
    try:
        return await GroupActions.update_group(group, group_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Delete a group

@router.delete("/{group_id}",
               tags=["Groups"],
               status_code=status.HTTP_204_NO_CONTENT,
               response_description="Delete a group")
@version(1)
async def delete_group(group: Group = Depends(Dependencies.get_group)):
    try:
        await GroupActions.delete_group(group)
        return status.HTTP_204_NO_CONTENT
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get a list of group members

@router.get("/{group_id}/members",
            tags=["Group Members"],
            response_description="List of group members",
            response_model=MemberSchemas.MemberList,
            response_model_exclude_unset=True)
@version(1)
async def get_group_members(group: Group = Depends(Dependencies.get_group)):
    try:
        return await MembersActions.get_members(group)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Add member to group

@router.post("/{group_id}/members",
             tags=["Group Members"],
             response_description="List of group members",
             response_model=MemberSchemas.MemberList)
@version(1)
async def add_group_members(member_data: MemberSchemas.AddMembers,
                            group: Group = Depends(Dependencies.get_group)):
    try:
        return await MembersActions.add_members(group, member_data.accounts)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Remove members from the workspace

@router.delete("/{group_id}/members/{member_id}",
               tags=["Group Members"],
               response_description="Updated list removed members",
               response_model_exclude_unset=True)
@version(1)
async def remove_group_member(group: Group = Depends(Dependencies.get_group),
                              member: Member = Depends(Dependencies.get_member)):
    try:
        return await MembersActions.remove_member(group, account)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all policies in the workspace

@router.get("/{group_id}/policies",
            tags=["Group Policies"],
            response_description="List of all policies",
            response_model=PolicySchemas.PolicyList)
@version(1)
async def get_group_policies(group: Group = Depends(Dependencies.get_group),
                             account_id: ResourceID = Query(None)) -> PolicySchemas.PolicyList:
    try:
        account = await Dependencies.get_account(account_id) if account_id else None
        member = await Dependencies.get_member(account, group) if account else None
        return await PolicyActions.get_policies(resource=group, policy_holder=member)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Set permissions for a user in a group

@router.put("/{group_id}/policies/{policy_id}",
            tags=["Group Policies"],
            response_description="Updated policy",
            response_model=PolicySchemas.PolicyOutput)
@version(1)
async def set_group_policy(group: Group = Depends(Dependencies.get_group),
                           policy: Policy = Depends(Dependencies.get_policy),
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
        return await PolicyActions.update_policy(policy, new_permissions=permissions.permissions)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get All Group Permissions

@router.get("/permissions",
            tags=["Groups"],
            response_description="List of all Group permissions",
            response_model=PolicySchemas.PermissionList)
@version(1)
async def get_group_permissions():
    try:
        return await PermissionsActions.get_group_permissions()
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))
