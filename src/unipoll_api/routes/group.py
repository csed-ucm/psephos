# FastAPI
from typing import Annotated, Literal
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from unipoll_api import dependencies as Dependencies
from unipoll_api import AccountManager
from unipoll_api.actions import GroupActions, PermissionsActions, MembersActions, PolicyActions
from unipoll_api.exceptions.resource import APIException
from unipoll_api.schemas import GroupSchemas, PolicySchemas, MemberSchemas
from unipoll_api.documents import Account, Group, Policy, ResourceID


# APIRouter creates path operations for user module
open_router: APIRouter = APIRouter()
router: APIRouter = APIRouter(dependencies=[Depends(Dependencies.check_group_permission)])


# Get groups
@open_router.get("/", response_description="List of groups")
async def get_all_groups(workspace: Annotated[ResourceID | None, Query()] = None,
                         account: Annotated[ResourceID | None, Query()] = None,
                         name: Annotated[str | None, Query()] = None
                         ) -> GroupSchemas.GroupList:
    return await GroupActions.get_groups(workspace=await Dependencies.get_workspace(workspace) if workspace else None,
                                         account=await Dependencies.get_account(account) if account else None,
                                         name=name)


# Create a new group
@open_router.post("/",
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


# Get a list of group members
@router.get("/{group_id}/members",
            response_description="List of group members",
            response_model=MemberSchemas.MemberList,
            response_model_exclude_unset=True)
async def get_group_members(group: Group = Depends(Dependencies.get_group)):
    try:
        return await MembersActions.get_members(group)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Add member to group
@router.post("/{group_id}/members",
             response_description="List of group members",
             response_model=MemberSchemas.MemberList)
async def add_group_members(member_data: MemberSchemas.AddMembers,
                            group: Group = Depends(Dependencies.get_group)):
    try:
        return await MembersActions.add_members(group, member_data.accounts)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Remove members from the workspace
@router.delete("/{group_id}/members/{account_id}",
               response_description="Updated list removed members",
               response_model_exclude_unset=True)
async def remove_group_member(group: Group = Depends(Dependencies.get_group),
                              account: Account = Depends(Dependencies.get_account)):
    try:
        return await MembersActions.remove_member(group, account)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List all policies in the workspace
@router.get("/{group_id}/policies",
            response_description="List of all policies",
            response_model=PolicySchemas.PolicyList,)
async def get_group_policies(group: Group = Depends(Dependencies.get_group)) -> PolicySchemas.PolicyList:
    try:
        return await PolicyActions.get_policies(resource=group)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# List user's permissions in the group
@router.get("/{group_id}/policy",
            response_description="List of all member policies",
            response_model=PolicySchemas.PolicyOutput)
async def get_group_policy(group: Group = Depends(Dependencies.get_group),
                           account_id: ResourceID | None = None):
    try:
        account = await Dependencies.get_account(account_id) if account_id else AccountManager.active_user.get()
        policy_list = await PolicyActions.get_policies(resource=group, policy_holder=account)
        policy = policy_list.policies[0]
        return PolicySchemas.PolicyOutput(**policy.model_dump())
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Set permissions for a user in a group
@router.put("/{group_id}/policy",
            response_description="Updated policy",
            response_model=PolicySchemas.PolicyOutput)
async def set_group_policy(group: Group = Depends(Dependencies.get_group),
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
        # return await GroupActions.set_group_policy(group, permissions)

        policy = None
        if permissions.policy_id:
            policy = await Dependencies.get_policy(permissions.policy_id)  # type: ignore
        elif permissions.account_id:
            account = await Dependencies.get_account(permissions.account_id)
            # policy = await Policy.find_one(Policy.policy_holder.id == account.id, fetch_links=True)
            # Temporarily workaround
            policy_list = await PolicyActions.get_policies(resource=group, policy_holder=account)  # type: ignore
            policy = policy_list.policies[0]  # type: ignore
            policy = await Policy.get(policy.id, fetch_links=True)  # type: ignore
        elif permissions.group_id:
            # Temporarily workaround
            group = await Dependencies.get_group(permissions.group_id)
            policy_list = await PolicyActions.get_policies(resource=group, policy_holder=group)  # type: ignore
            policy = policy_list.policies[0]  # type: ignore
            policy = await Policy.get(policy.id, fetch_links=True)  # type: ignore

        if not policy:
            raise APIException(404, "Policy not found 404")

        return await PolicyActions.update_policy(policy, new_permissions=permissions.permissions)
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
