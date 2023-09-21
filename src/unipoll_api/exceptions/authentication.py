from fastapi import status
from unipoll_api.exceptions import resource
# from app.models.documents import ResourceID


class InvalidAuthorizationHeader(resource.APIException):
    def __init__(self):
        super().__init__(code=status.HTTP_400_BAD_REQUEST,
                         detail="Invalid Authorization header")


class InvalidAccessToken(resource.APIException):
    def __init__(self):
        super().__init__(code=status.HTTP_401_UNAUTHORIZED,
                         detail="Invalid Access token")


class InvalidRefreshToken(resource.APIException):
    def __init__(self):
        super().__init__(code=status.HTTP_401_UNAUTHORIZED,
                         detail="Invalid Refresh token")


class refreshTokenExpired(resource.APIException):
    def __init__(self):
        super().__init__(code=status.HTTP_401_UNAUTHORIZED,
                         detail="Refresh token expired; Please login again")


class InvalidClientID(resource.APIException):
    def __init__(self):
        super().__init__(code=status.HTTP_401_UNAUTHORIZED,
                         detail="Invalid Client ID")
