from fastapi import APIRouter, Depends
from unipoll_api.dependencies import set_active_user

# Import endpoints defined in the routes directory
from . import account as AccountRoutes
from . import authentication as AuthenticationRoutes
from . import group as GroupRoutes
from . import workspace as WorkspaceRoutes

# Create main router
router: APIRouter = APIRouter()

# Add endpoints defined in the routes directory
router.include_router(WorkspaceRoutes.router,
                      prefix="/workspaces",
                      tags=["Workspaces"],
                      dependencies=[Depends(set_active_user)])
router.include_router(GroupRoutes.router,
                      prefix="/groups",
                      tags=["Groups"],
                      dependencies=[Depends(set_active_user)])
router.include_router(AccountRoutes.router,
                      prefix="/accounts",
                      tags=["Accounts"],
                      dependencies=[Depends(set_active_user)])
router.include_router(AuthenticationRoutes.router,
                      prefix="/auth",
                      tags=["Authentication"])