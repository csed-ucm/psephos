from fastapi import APIRouter, Depends
from unipoll_api import dependencies as Dependencies

# Import endpoints defined in the routes directory
from . import account as AccountRoutes
from . import authentication as AuthenticationRoutes
from . import group as GroupRoutes
from . import workspace as WorkspaceRoutes
from . import poll as PollRoutes

# Create main router
router: APIRouter = APIRouter()

# Add endpoints defined in the routes directory
router.include_router(AuthenticationRoutes.router,
                      prefix="/auth",
                      tags=["Authentication"])
router.include_router(AccountRoutes.router,
                      prefix="/accounts",
                      tags=["Accounts"],
                      dependencies=[Depends(Dependencies.set_active_user)])
router.include_router(WorkspaceRoutes.router,
                      prefix="/workspaces",
                      dependencies=[Depends(Dependencies.set_active_user)])
router.include_router(GroupRoutes.router,
                      dependencies=[Depends(Dependencies.set_active_user)])
router.include_router(PollRoutes.router,
                      dependencies=[Depends(Dependencies.set_active_user)])
