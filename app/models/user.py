from typing import List
# from beanie import PydanticObjectId
from fastapi_users.db import BeanieBaseUser
from pydantic import Field
from app.schemas.user import UserID
from app.schemas.group import GroupID


class User(BeanieBaseUser[UserID]):
    id: UserID = Field(default_factory=UserID, alias="_id")
    groups: List[GroupID] = []
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
