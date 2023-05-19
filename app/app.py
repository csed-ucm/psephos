from fastapi import FastAPI, Depends
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie
from app.mongo_db import mainDB, DOCUMENT_MODELS
from app.routes import workspace as WorkspaceRoutes
from app.routes import group as GroupRoutes
from app.routes import account as AccountRoutes
from app.config import get_settings
from app.schemas.account import Account, CreateAccount, UpdateAccount
from app.account_manager import auth_backend, fastapi_users
from app.dependencies import set_active_user


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="A REST API to manage users and polls",
    version=settings.app_version,
)


app.include_router(WorkspaceRoutes.open_router,
                   prefix="/workspaces",
                   tags=["Workspaces"],
                   dependencies=[Depends(set_active_user)])
app.include_router(WorkspaceRoutes.router,
                   prefix="/workspaces",
                   tags=["Workspaces"],
                   dependencies=[Depends(set_active_user)])
app.include_router(GroupRoutes.router,
                   prefix="/groups",
                   tags=["Groups"],
                   dependencies=[Depends(set_active_user)])
app.include_router(AccountRoutes.router,
                   prefix="/accounts",
                   tags=["Accounts"],
                   dependencies=[Depends(set_active_user)])
app.include_router(fastapi_users.get_auth_router(auth_backend),
                   prefix="/auth/jwt",
                   tags=["Authentication"])
app.include_router(fastapi_users.get_register_router(Account, CreateAccount),
                   prefix="/auth",
                   tags=["Auth"])
app.include_router(fastapi_users.get_reset_password_router(),
                   prefix="/auth",
                   tags=["Auth"])
app.include_router(fastapi_users.get_verify_router(Account),
                   prefix="/auth",
                   tags=["Auth"])
app.include_router(fastapi_users.get_users_router(Account, UpdateAccount),
                   prefix="/accounts",
                   tags=["Accounts"])


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def on_startup() -> None:
    # Simplify operation IDs so that generated API clients have simpler function names
    # Each route will have its operation ID set to the method name
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name

    await init_beanie(
        database=mainDB,
        document_models=DOCUMENT_MODELS,
    )
