from fastapi import APIRouter, HTTPException, Depends
from unipoll_api import dependencies as Dependencies
from unipoll_api.account_manager import active_user
from unipoll_api.documents import Account, Workspace, Member, Group
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
async def get_member_permissions(member: Member = Depends(Dependencies.get_member)):
    try:
        
        await member.fetch_all_links()        
        workspace = member.workspace
        
        workspace_permissions = await Permissions.get_all_permissions(workspace, member)
        group_permissions = {}
        poll_permissions = {}
        for group in workspace.groups:
            group_permissions[group.id] = await Permissions.get_all_permissions(group, member)
        for poll in workspace.polls:
            poll_permissions[poll.id] = await Permissions.get_all_permissions(poll, member)
        
        return {
            # "permissions": {
                "workspace": {
                    "id": str(workspace.id),
                    "permissions": Permissions.convert_permission_to_string(workspace_permissions, "Workspace"),
                },
                "groups": [ {
                        "id": str(group_id),
                        "permissions": Permissions.convert_permission_to_string(permissions, "Group")
                    } for group_id, permissions in group_permissions.items() 
                ],
                "polls": [ {
                        "id": str(poll_id),
                        "permissions": Permissions.convert_permission_to_string(permissions, "Poll")
                    } for poll_id, permissions in poll_permissions.items() 
                ]
            # }
        }
        
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))