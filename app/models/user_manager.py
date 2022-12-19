from typing import Optional, AsyncGenerator
from beanie import PydanticObjectId
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (AuthenticationBackend,
                                          BearerTransport,
                                          JWTStrategy)
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from app.models.user import User
from app.mongo_db import get_user_db

# from devtools import debug
from app.utils import colored_dbg

SECRET = "SECRET"


class UserManager(ObjectIDIDMixin,
                  BaseUserManager[User, PydanticObjectId]):  # type: ignore
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User,
                                request: Optional[Request] = None) -> None:
        # print(f"User {user.id} has registered.")
        colored_dbg.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str,
                                       request: Optional[Request] = None
                                       ) -> None:
        colored_dbg.info(
            f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str,
                                      request: Optional[Request] = None
                                      ) -> None:
        colored_dbg.info(
            "Verification requested for user {}. \
            Verification token: {}".format(user.id, token))

    async def on_before_delete(self, user: User,
                               request: Optional[Request] = None) -> None:
        colored_dbg.info(
            f"User {user.id} is going to be deleted, cleaning up their data.")
        # TODO: Delete all groups that the user owns
        # for group in user.groups:
        # await group.delete()


async def get_user_manager(user_db:
                           BeanieUserDatabase[User, PydanticObjectId]
                           = Depends(get_user_db)) -> AsyncGenerator[
                               BaseUserManager[User,  # type: ignore
                                               PydanticObjectId],
                               None]:
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
# cookie_transport = CookieTransport(cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, PydanticObjectId](  # type: ignore
    get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
