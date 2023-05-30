from contextvars import ContextVar
from typing import Optional, AsyncGenerator
from beanie import PydanticObjectId, Document
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (AuthenticationBackend,
                                          BearerTransport, CookieTransport,
                                          JWTStrategy)
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from fastapi_users_db_beanie.access_token import BeanieAccessTokenDatabase, BeanieBaseAccessToken
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy
from app.models.documents import Account
from app.utils import colored_dbg

SECRET = "SECRET"

UserManager = BaseUserManager[Account, PydanticObjectId]  # type: ignore


class AccountManager(ObjectIDIDMixin, UserManager):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: Account,
                                request: Optional[Request] = None) -> None:
        # print(f"Account {user.id} has registered.")
        colored_dbg.info(f"Account {user.id} has registered.")

    async def on_after_forgot_password(self, user: Account, token: str,
                                       request: Optional[Request] = None
                                       ) -> None:
        colored_dbg.info(
            f"Account {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: Account, token: str,
                                      request: Optional[Request] = None
                                      ) -> None:
        colored_dbg.info(
            "Verification requested for user {}. \
            Verification token: {}".format(user.id, token))

    async def on_before_delete(self, user: Account,
                               request: Optional[Request] = None) -> None:
        colored_dbg.info(
            f"Account {user.id} is going to be deleted, cleaning up their data.")


class AccessToken(BeanieBaseAccessToken, Document):
    pass


async def get_account_db() -> AsyncGenerator:
    yield BeanieUserDatabase(Account)  # type: ignore


async def get_user_manager(user_db=Depends(get_account_db)) -> AsyncGenerator[UserManager, None]:
    yield AccountManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


async def get_access_token_db():
    yield BeanieAccessTokenDatabase(AccessToken)  # type: ignore


def get_database_strategy(
        access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db)  # type: ignore
        ) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    # transport=cookie_transport,
    # get_strategy=get_jwt_strategy,
    get_strategy=get_database_strategy,
)

fastapi_users = FastAPIUsers[Account, PydanticObjectId](get_user_manager, [auth_backend])  # type: ignore

get_current_active_user = fastapi_users.current_user(active=True)
current_active_user = ContextVar("current_active_user")
