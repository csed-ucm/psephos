from typing import Optional
from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    scope: Optional[str] = None
    client_id: Optional[str] = None
    expires_in: int = 3600
    refresh_token: str


class PostmanRefreshTokenRequest(BaseModel):
    refresh_token: str
    grant_type: str = "refresh_token"
