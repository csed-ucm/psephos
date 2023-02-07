from fastapi import FastAPI, Depends
from beanie import init_beanie
from fastapi.middleware.cors import CORSMiddleware
from app.mongo_db import mainDB
# import app.routes as routes
# from app.routes import group, user, workspace
from app.routes import workspace
from app.config import get_settings
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.models.user_manager import auth_backend, fastapi_users, get_current_active_user, current_active_user
from app.models.workspace import Workspace
from app.models.user import User
from app.models.group import Group
settings = get_settings()


# Get all workspaces
async def set_active_user(user_account: User = Depends(get_current_active_user)):
    current_active_user.set(user_account)
    return user_account

app = FastAPI(
    title=settings.app_name,
    description="A REST API to manage users and polls",
    version=settings.app_version,
)

app.include_router(workspace.router,
                   prefix="/workspaces",
                   tags=["Workspaces"],
                   dependencies=[Depends(set_active_user)])
app.include_router(fastapi_users.get_auth_router(auth_backend),
                   prefix="/auth/jwt",
                   tags=["Auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate),
                   prefix="/auth",
                   tags=["Auth"])
app.include_router(fastapi_users.get_reset_password_router(),
                   prefix="/auth",
                   tags=["Auth"])
app.include_router(fastapi_users.get_verify_router(UserRead),
                   prefix="/auth",
                   tags=["Auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate),
                   prefix="/users",
                   tags=["Users"])


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
    await init_beanie(
        database=mainDB,
        document_models=[
            # BUG: Incompatible type "Type[Group]"; expected "Union[Type[View], str]"
            User,  # type: ignore
            Group,  # type: ignore
            Workspace
        ],
    )
