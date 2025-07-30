from fastapi import APIRouter, HTTPException
from unipoll_api.schemas import PolicySchemas
from unipoll_api.exceptions.resource import APIException
from unipoll_api.actions.__interface__ import PermissionsActions

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
