from fastapi import FastAPI, Depends
from beanie import init_beanie
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from app.mongo_db import mainDB
from app import routes
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.models.user_manager import auth_backend, current_active_user, fastapi_users
from app.models.user import User
from app.models.group import Group

load_dotenv()

app = FastAPI(
    title="Polling App",
    description="A REST API to manage users and polls",
    version="1.0.0",
)

app.include_router(routes.group.router)
app.include_router(routes.user.router)
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
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
@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    await init_beanie(
        database=mainDB,
        document_models=[
            User,
            Group
        ],
    )