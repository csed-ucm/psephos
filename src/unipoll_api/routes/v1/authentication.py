from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users.authentication import Strategy

from unipoll_api import account_manager as AccountManager

# import fastapi_users, get_user_manager, jwt_backend, get_database_strategy, get_access_token_db
from unipoll_api.actions import authentication as AuthActions
# from unipoll_api.schemas import authentication as AuthSchemas
from unipoll_api.schemas import account as AccountSchemas
from unipoll_api.exceptions.resource import APIException
from unipoll_api.utils.token_db import BeanieAccessTokenDatabase
router: APIRouter = APIRouter()


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
    **AccountManager.jwt_backend.transport.get_openapi_login_responses_success(),
}


@router.post(
    "/jwt/login",
    name=f"auth:{AccountManager.jwt_backend.name}.login",
    responses=login_responses,
    response_model_exclude_unset=True
)
async def login(credentials: OAuth2PasswordRequestForm = Depends(),
                user_manager: BaseUserManager[models.UP, models.ID] = Depends(AccountManager.get_user_manager),
                token_db: BeanieAccessTokenDatabase = Depends(AccountManager.get_access_token_db),
                strategy: Strategy = Depends(AccountManager.get_database_strategy)):
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

    return await AccountManager.jwt_backend.login(strategy, user)


# Refresh the access token using the refresh token
@router.post("/jwt/refresh", responses=login_responses, response_model_exclude_unset=True)
async def refresh_jwt(authorization: Annotated[str, Header(...)],
                      refresh_token: Annotated[str, Header(...)],
                      token_db: BeanieAccessTokenDatabase = Depends(AccountManager.get_access_token_db),
                      strategy: Strategy = Depends(AccountManager.get_database_strategy)):
    """Refresh the access token using the refresh token.

    Headers:
        authorization: `Authorization` header with the access token
        refresh_token: `Refresh-Token` header with the refresh token
    """
    try:
        return await AuthActions.refresh_token(authorization, refresh_token)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=e.detail)


# Refresh the access token using the refresh token and Client ID
@router.post("/jwt/postman_refresh", responses=login_responses, response_model_exclude_unset=True)
async def refresh_jwt_with_client_ID(authorization: Annotated[str, Header(...)],
                                     body: Annotated[str, Body(...)],
                                     token_db: BeanieAccessTokenDatabase = Depends(AccountManager.get_access_token_db),
                                     strategy: Strategy = Depends(AccountManager.get_database_strategy)):
    """Refresh the access token using the refresh token.

    Headers:
        authorization: `Authorization` header with the access token
    Body:
        refresh_token: `Refresh-Token` header with the refresh token
    """
    try:
        # import json
        # print(body.decode('utf-8'))
        # body = json.loads(body.decode('utf-8'))
        # print(body)
        # AuthSchemas.PostmanRefreshTokenRequest(**body)
        return await AuthActions.refresh_token_with_clientID(authorization, body, token_db, strategy)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=e.detail)


# Include prebuilt routes for authentication
router.include_router(AccountManager.fastapi_users.get_register_router(
    AccountSchemas.Account, AccountSchemas.CreateAccount))
router.include_router(AccountManager.fastapi_users.get_reset_password_router())
router.include_router(AccountManager.fastapi_users.get_verify_router(AccountSchemas.Account))
