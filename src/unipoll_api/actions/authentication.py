import re
import base64
from beanie import PydanticObjectId

from fastapi import Depends

from unipoll_api.documents import Account
from unipoll_api.exceptions import AuthExceptions, AccountExceptions
from unipoll_api.utils import colored_dbg as Debug
from unipoll_api.account_manager import jwt_backend, get_database_strategy, get_access_token_db


async def refresh_token(authorization: str,
                        refresh_token: str,
                        token_db=Depends(get_access_token_db),
                        strategy=Depends(get_database_strategy)):
    # Make sure the Authorization header is valid and extract the access token
    try:
        access_token = re.match(r'^Bearer ([A-z0-9\-]+)$', authorization).group(1)  # type: ignore
    except Exception as e:
        Debug.print_error(str(e))
        raise AuthExceptions.InvalidAuthorizationHeader()

    # Get the token data from the database using the access token
    # NOTE: We do not supply a max_age parameter in case access tokens has already expired
    token_data = await token_db.get_by_token(access_token)

    # Make sure the access token exists in the database
    if token_data is None:
        raise AuthExceptions.InvalidAccessToken()

    # Make sure the access token is associated with the supplied refresh token
    if token_data.refresh_token != refresh_token:
        raise AuthExceptions.InvalidRefreshToken()

    # Get the user from the database using the user ID in the token data
    user = await Account.get(token_data.user_id)
    if user is None:
        raise AccountExceptions.AccountNotFound(token_data.user_id)

    # Check if the refresh token is the most recent one
    all_tokens = await token_db.get_token_family_by_user_id(user.id)
    if (await all_tokens.to_list())[0].refresh_token != refresh_token:
        # If not, delete all tokens associated with the user and return an error
        await strategy.destroy_token_family(user)
        raise AuthExceptions.refreshTokenExpired()

    # Login the user using the supplied strategy
    # Generate new pair of access and refresh tokens
    # Returns Response object with LoginResponse schema
    return await jwt_backend.login(strategy, user)


async def refresh_token_with_clientID(authorization: str,
                                      body: str,
                                      token_db=Depends(get_access_token_db),
                                      strategy=Depends(get_database_strategy)):
    # Make sure the Authorization header is valid and extract the access token
    try:
        client_id = re.match(r'^Basic (\S+)$', authorization).group(1)  # type: ignore
        refresh_token = re.match(r'^refresh_token=(\S+)&grant_type=refresh_token$', body).group(1)  # type: ignore
    except Exception as e:
        Debug.print_error(str(e))
        raise AuthExceptions.InvalidAuthorizationHeader()

    # Get the token data from the database using the access token
    token_data = await token_db.get_by_refresh_token(refresh_token)

    # Make sure the access token exists in the database
    if token_data is None:
        raise AuthExceptions.InvalidAccessToken()

    # Get the user from the database using the user ID in the token data
    user = await Account.get(token_data.user_id)
    if user is None:
        raise AccountExceptions.AccountNotFound(token_data.user_id)

    # Decode the client ID and make sure it matches account ID
    client_id = base64.b64decode(client_id)
    if PydanticObjectId(str(client_id, "utf-8")[:-1]) != user.id:
        raise AuthExceptions.InvalidClientID()

    # Check if the refresh token is the most recent one
    all_tokens = await token_db.get_token_family_by_user_id(user.id)
    if (await all_tokens.to_list())[0].refresh_token != refresh_token:
        # If not, delete all tokens associated with the user and return an error
        await strategy.destroy_token_family(user)
        raise AuthExceptions.refreshTokenExpired()

    # Login the user using the supplied strategy
    # Generate new pair of access and refresh tokens
    # Returns Response object with LoginResponse schema
    return await jwt_backend.login(strategy, user)
