from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users.authentication import Strategy

from app.account_manager import fastapi_users, get_current_active_user, get_user_manager
from app.account_manager import jwt_backend, get_database_strategy, get_access_token_db
from app.schemas.account import Account, CreateAccount
from app.schemas import authentication as AuthSchemas

router = APIRouter()


router.include_router(fastapi_users.get_register_router(Account, CreateAccount))
router.include_router(fastapi_users.get_reset_password_router())
router.include_router(fastapi_users.get_verify_router(Account))
# router.include_router(fastapi_users.get_auth_router(jwt_backend), prefix="/jwt")


@router.post("/jwt/refresh")
async def refresh_jwt(response: Response,
                      token_db=Depends(get_access_token_db),
                      user=Depends(get_current_active_user)):

    res = await jwt_backend.login(strategy=get_database_strategy(token_db), user=user)
    return res


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
    token = await strategy.write_token(user)

    return AuthSchemas.LoginOutput(access_token=token, refresh_token=token)
