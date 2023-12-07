from click import group
from fastapi import APIRouter, HTTPException, Depends
from unipoll_api import dependencies as Dependencies
from unipoll_api.documents import Account, Workspace, Member
from unipoll_api.schemas import PolicySchemas
from unipoll_api.exceptions.resource import APIException
from unipoll_api.actions import PermissionsActions
from unipoll_api.utils import Permissions


router = APIRouter()


# Get All Workspace Permissions
@router.get("/workspaces",
            response_description="List of all workspace permissions",
            response_model=PolicySchemas.PermissionList)
async def get_workspace_permissions():
    try:
        return await PermissionsActions.get_workspace_permissions()
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get All Group Permissions
@router.get("/groups",
            response_description="List of all Group permissions",
            response_model=PolicySchemas.PermissionList)
async def get_group_permissions():
    try:
        return await PermissionsActions.get_group_permissions()
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


@router.get("/members/{member_id}",
            response_description="List of all member permissions")
async def get_member_permissions(member: Member = Depends(Dependencies.get_member),
                                 workspace: Workspace = Depends(Dependencies.get_workspace)):
    try:
        workspace_permissions = await Permissions.get_all_permissions(member, workspace)
        group_permissions = {}
        for group in member.groups:
            group_permissions[group.id] = await Permissions.get_all_permissions(member, group)
        
        return {
            "permissions": {
                "workspace": {
                    "id": workspace.id,
                    "permissions": workspace_permissions,
                },
                "groups": [ {
                        "id": group.id,
                        "permissions": group_permissions[group.id]
                    } for group in member.groups 
                ]
            }
        }
        
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))