from fastapi import FastAPI
from beanie import init_beanie
from fastapi.middleware.cors import CORSMiddleware
from app.mongo_db import mainDB
# import app.routes as routes
from app.routes import group, user
from app.config import get_settings
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.models.user_manager import auth_backend, fastapi_users
from app.models.user import User
from app.models.group import Group

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="A REST API to manage users and polls",
    version=settings.app_version,
)

app.include_router(group.router)
app.include_router(user.router)
app.include_router(fastapi_users.get_auth_router(
    auth_backend), prefix="/auth/jwt", tags=["Auth"])
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["Auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["Auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["Users"],
)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# @app.get("/authenticated-route")
# async def authenticated_route(user: User = Depends(current_active_user)) -:
#     return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup() -> None:
    await init_beanie(
        database=mainDB,
        document_models=[
            # BUG: Incompatible type "Type[Group]"; expected "Union[Type[View], str]"
            User,  # type: ignore
            Group  # type: ignore
        ],
    )
