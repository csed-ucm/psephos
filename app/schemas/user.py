from beanie import PydanticObjectId
from fastapi_users import schemas
from pydantic import Field, EmailStr, BaseModel

# TODO: Look into replacing email[str] with email[EmailStr]


# class UserRead(schemas.BaseUser[PydanticObjectId]):
class UserID(PydanticObjectId):
    @classmethod
    def __modify_schema__(cls, field_schema):  # type: ignore
        field_schema.update(
            type="string",
            example="5eb7cf5a86d9755df3a6c593")


class UserRead(schemas.BaseUser[UserID]):
    # email: EmailStr
    id: UserID = Field(...)
    email: EmailStr = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)


class UserReadBasicInfo(BaseModel):
    # email: EmailStr
    email: EmailStr = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)


class UserCreate(schemas.BaseUserCreate):
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

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "pass1234",
                "first_name": "John",
                "last_name": "Smith",
            }
        }


class UserAddToGroup(schemas.BaseUser):
    email: EmailStr = Field(...)
    role: str = Field(
        default="user",
        title="Role",
        description="Role of the user in the group",
        max_length=5,
        min_length=4,
        regex="^(user|admin)$")

    class Config:
        schema_extra = {
            "example": {
                "email": "email@example.com",
                "role": "admin",
            }
        }


class UserUpdate(schemas.BaseUserUpdate):
    pass
