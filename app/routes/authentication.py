from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users.authentication import Strategy

from app.account_manager import fastapi_users, get_user_manager
from app.account_manager import jwt_backend, get_database_strategy, get_access_token_db
from app.schemas import account as AccountSchemas
# from app.schemas import authentication as AuthSchemas
from app.models.documents import Account
from app.utils.token_db import BeanieAccessTokenDatabase
from app.utils.auth_strategy import DatabaseStrategy


import re

router = APIRouter()


router.include_router(fastapi_users.get_register_router(AccountSchemas.Account, AccountSchemas.CreateAccount))
# TODO: Invalidate all tokens associated with the user when they delete their account or reset their passwords
router.include_router(fastapi_users.get_reset_password_router())
router.include_router(fastapi_users.get_verify_router(AccountSchemas.Account))

# The Auth router is not included because we will be using our own custom auth router
# router.include_router(fastapi_users.get_auth_router(jwt_backend), prefix="/jwt")


@router.post("/jwt/refresh")
async def refresh_jwt(response: Response,
                      authorization: Annotated[str | None, Header()] = None,
                      refresh_token: Annotated[str | None, Header()] = None,
                      token_db: BeanieAccessTokenDatabase = Depends(get_access_token_db),
                      strategy: DatabaseStrategy = Depends(get_database_strategy)):
    # Make sure the Authorization header is valid and extract the access token
    try:
        access_token = re.match(r'^Bearer ([A-z0-9\-]+)$', authorization).group(1)  # type: ignore
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Authorization header")

    # Get the token data from the database using the access token
    # NOTE: We do not supply a max_age parameter in case access tokens has already expired
    token_data = await token_db.get_by_token(access_token)

    # Make sure the access token exists in the database
    if token_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    # Make sure the access token is associated with the supplied refresh token
    if token_data.refresh_token != refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

    # Get the user from the database using the user ID in the token data
    user = await Account.get(token_data.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not found")

    # Check if the refresh token is the most recent one
    all_tokens = await token_db.get_token_family_by_user_id(user.id)
    if (await all_tokens.to_list())[0].refresh_token != refresh_token:
        # If not, delete all tokens associated with the user and return an error
        await strategy.destroy_token_family(user)
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

    # Generate new pair of access and refresh tokens
    return await jwt_backend.login(strategy, user)


login_responses: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.LOGIN_BAD_CREDENTIALS: {
                        "summary": "Bad credentials or the user is inactive.",
                        "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                    },
                    ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                        "summary": "The user is not verified.",
                        "value": {"detail": ErrorCode.LOGIN_USER_NOT_VERIFIED},
                    },
                }
            }
        },
    },
    **jwt_backend.transport.get_openapi_login_responses_success(),
}


@router.post(
    "/jwt/login",
    name=f"auth:{jwt_backend.name}.login",
    responses=login_responses,
)
async def login(
    request: Request,
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    strategy: Strategy[models.UP, models.ID] = Depends(jwt_backend.get_strategy),
):
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )
    # if requires_verification and not user.is_verified:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
    #     )

    return await jwt_backend.login(strategy, user)
