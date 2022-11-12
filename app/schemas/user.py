from beanie import PydanticObjectId
from fastapi_users import schemas
from pydantic import Field

class UserRead(schemas.BaseUser[PydanticObjectId]):
    first_name: str = Field(default_factory=str, max_length=20, min_length=2, regex="^[A-Z][a-z]*$")
    last_name: str = Field(default_factory=str, max_length=20, min_length=2, regex="^[A-Z][a-z]*$")

class UserCreate(schemas.BaseUserCreate):
    first_name: str = Field(default_factory=str, max_length=20, min_length=2, regex="^[A-Z][a-z]*$")
    last_name: str = Field(default_factory=str, max_length=20, min_length=2, regex="^[A-Z][a-z]*$")


class UserUpdate(schemas.BaseUserUpdate):
    pass