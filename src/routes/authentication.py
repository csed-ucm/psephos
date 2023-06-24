from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users.authentication import Strategy

from src.account_manager import fastapi_users, get_user_manager, jwt_backend, get_database_strategy, get_access_token_db
from src.actions import authentication as AuthActions
from src.schemas import account as AccountSchemas
from src.exceptions.resource import APIException
# from app.schemas import authentication as AuthSchemas
from src.utils.token_db import BeanieAccessTokenDatabase
from src.utils.auth_strategy import DatabaseStrategy
router = APIRouter()


# TODO: Invalidate all tokens associated with the user when they delete their account or reset their passwords


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


# Refresh the access token using the refresh token
@router.post("/jwt/refresh")
async def refresh_jwt(response: Response,
                      authorization: Annotated[str | None, Header()] = None,
                      refresh_token: Annotated[str | None, Header()] = None,
                      token_db: BeanieAccessTokenDatabase = Depends(get_access_token_db),
                      strategy: DatabaseStrategy = Depends(get_database_strategy)):
    """Refresh the access token using the refresh token.

    Headers:
        authorization: `Authorization` header with the access token
        refresh_token: `Refresh-Token` header with the refresh token
    """
    try:
        return await AuthActions.refresh_token(authorization, refresh_token, token_db, strategy)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=e.detail)


# Include prebuilt routes for authentication
router.include_router(fastapi_users.get_register_router(AccountSchemas.Account, AccountSchemas.CreateAccount))
router.include_router(fastapi_users.get_reset_password_router())
router.include_router(fastapi_users.get_verify_router(AccountSchemas.Account))
