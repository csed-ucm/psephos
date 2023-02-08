from fastapi_users.db import BeanieBaseUser
from pydantic import Field
from app.schemas.user import UserID


class User(BeanieBaseUser[UserID]):
    id: UserID = Field(default_factory=UserID, alias="_id")
    first_name: str = Field(
        default_factory=str,
        max_length=20,
        min_length=2,
        regex="^[A-Z][a-z]*$")
    last_name: str = Field(
        default_factory=str,
        max_length=20,
        min_length=2,
        regex="^[A-Z][a-z]*$")
