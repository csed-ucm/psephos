# FastAPI
from typing import Annotated, Literal
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from unipoll_api import dependencies as Dependencies
from unipoll_api.actions.__interface__ import GroupActions, PermissionsActions, MembersActions, PolicyActions
from unipoll_api.exceptions.resource import APIException
from unipoll_api.schemas import GroupSchemas, PolicySchemas, MemberSchemas
from unipoll_api.documents import Group, Policy, ResourceID, Member, Workspace
from unipoll_api.utils import Permissions
from unipoll_api import AccountManager


router = APIRouter()

query_params = list[Literal["workspace", "policies", "members", "all"]]


# List all groups in the workspace
@router.get("/{workspace_id}/groups",
            tags=["Groups"],
            response_description="List of all groups",
            response_model=GroupSchemas.GroupList)
async def get_groups(workspace: Workspace = Depends(Dependencies.get_workspace)):
    try:
        return await GroupActions.get_groups(workspace)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all groups in the workspace
@router.post("/{workspace_id}/groups",
             status_code=201,
             tags=["Groups"],
             response_description="Created Group",
             response_model=GroupSchemas.GroupCreateOutput)
async def create_group(workspace: Workspace = Depends(Dependencies.get_workspace),
                       input_data: GroupSchemas.GroupCreateInput = Body(...)):
    try:
        return await GroupActions.create_group(workspace, input_data.name, input_data.description)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get group info by id
@router.get("/workspaces/{workspace_id}/groups/{group_id}",
            tags=["Groups"],
            response_description="Get a group",
            response_model=GroupSchemas.Group,
            response_model_exclude_defaults=True,
            response_model_exclude_none=True)
async def get_group(workspace: Workspace = Depends(Dependencies.get_workspace),
                    group: Group = Depends(Dependencies.get_group),
                    include: Annotated[query_params | None, Query()] = None):
    try:
        params = {}
        if include:
            if "all" in include:
                # params = {"include_members": True, "include_policies": True}
                params = {"include_" + param: True for param in ["members", "policies", "workspace"]}
            else:
                if "members" in include:
                    params["include_members"] = True
                if "policies" in include:
                    params["include_policies"] = True
                if "workspaces" in include:
                    params["include_workspaces"] = True
        return await GroupActions.get_group(group, **params)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Update group info

@router.patch("/workspaces/{workspace_id}/groups/{group_id}",
              tags=["Groups"],
              response_description="Update a group",
              response_model=GroupSchemas.GroupShort)
async def update_group(group_data: GroupSchemas.GroupUpdateRequest,
                       group: Group = Depends(Dependencies.get_group),
                       workspace: Workspace = Depends(Dependencies.get_workspace)):
    try:
        return await GroupActions.update_group(group, group_data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Delete a group

@router.delete("/workspaces/{workspace_id}/groups/{group_id}",
               tags=["Groups"],
               status_code=status.HTTP_204_NO_CONTENT,
               response_description="Delete a group")
async def delete_group(workspace: Workspace = Depends(Dependencies.get_workspace),
                       group: Group = Depends(Dependencies.get_group)):
    try:
        await GroupActions.delete_group(group)
        return status.HTTP_204_NO_CONTENT
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get a list of group members

@router.get("/workspaces/{workspace_id}/groups/{group_id}/members",
            tags=["Group Members"],
            response_description="List of group members",
            response_model=MemberSchemas.MemberList,
            response_model_exclude_unset=True)
async def get_group_members(workspace: Workspace = Depends(Dependencies.get_workspace),
                            group: Group = Depends(Dependencies.get_group)):
    try:
        return await MembersActions.get_members(group)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Add member to group

@router.post("/workspaces/{workspace_id}/groups/{group_id}/members",
             tags=["Group Members"],
             response_description="List of group members",
             response_model=MemberSchemas.MemberList)
async def add_group_members(member_data: MemberSchemas.AddMembers,
                            workspace: Workspace = Depends(Dependencies.get_workspace),
                            group: Group = Depends(Dependencies.get_group)):
    try:
        return await MembersActions.add_members(group, member_data.accounts)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Remove members from the workspace

@router.delete("/workspaces/{workspace_id}/groups/{group_id}/members/{member_id}",
               tags=["Group Members"],
               response_description="Updated list removed members",
               response_model_exclude_unset=True)
async def remove_group_member(workspace: Workspace = Depends(Dependencies.get_workspace),
                              group: Group = Depends(Dependencies.get_group),
                              member: Member = Depends(Dependencies.get_member)):
    try:
        return await MembersActions.remove_member(group, member)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all policies in the workspace

@router.get("/workspaces/{workspace_id}/groups/{group_id}/policies",
            tags=["Group Policies"],
            response_description="List of all policies",
            response_model=PolicySchemas.PolicyList)
async def get_group_policies(workspace: Workspace = Depends(Dependencies.get_workspace),
                             group: Group = Depends(Dependencies.get_group),
                             account_id: ResourceID = Query(None)) -> PolicySchemas.PolicyList:
    try:
        account = await Dependencies.get_account(account_id) if account_id else None
        member = await Dependencies.get_member_by_account(account, group) if account else None
        return await PolicyActions.get_policies(resource=group, policy_holder=member)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Set permissions for a user in a group

@router.put("/workspaces/{workspace_id}/groups/{group_id}/policies/{policy_id}",
            tags=["Group Policies"],
            response_description="Updated policy",
            response_model=PolicySchemas.PolicyOutput)
async def set_group_policy(workspace: Workspace = Depends(Dependencies.get_workspace),
                           group: Group = Depends(Dependencies.get_group),
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


# Get All Member Permissions in the Group
@router.get("/workspaces/{workspace_id}/groups/{group_id}/permissions",
            tags=["Group Permissions"],
            response_description="List of all member permissions in the workspace",
            response_model=PolicySchemas.PermissionList)
async def get_group_member_permissions(workspace: Workspace = Depends(Dependencies.get_workspace),
                                       group: Group = Depends(Dependencies.get_group)):
    try:
        account = AccountManager.active_user.get()
        member = await Dependencies.get_member_by_account(account, group.workspace)  # type: ignore
        group_permissions = await Permissions.get_all_permissions(group, member)
        return PolicySchemas.PermissionList(permissions=Permissions.convert_permission_to_string(group_permissions, "Group"))
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))