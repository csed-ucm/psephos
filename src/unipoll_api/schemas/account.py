from fastapi_users import schemas
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from unipoll_api.documents import ResourceID


class Account(schemas.BaseUser[ResourceID]):
    id: ResourceID = Field(...)
    email: EmailStr = Field(...)
    first_name: str = Field(
        default_factory=str,
        max_length=20,
        min_length=2,
        pattern="^[A-Z][a-z]*$")
    last_name: str = Field(
        default_factory=str,
        max_length=20,
        min_length=2,
        pattern="^[A-Z][a-z]*$")
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "user@example.com",
            "password": "pass1234",
            "first_name": "John",
            "last_name": "Smith",
        }
    })


class AccountShort(BaseModel):
    id: ResourceID
    email: EmailStr
    first_name: str
    last_name: str


class AccountList(BaseModel):
    accounts: list[AccountShort]


class CreateAccount(schemas.BaseUserCreate):
    email: EmailStr = Field(...)
    first_name: str = Field(
        default_factory=str,
        max_length=20,
        min_length=2,
        pattern="^[A-Z][a-z]*$")
    last_name: str = Field(
        default_factory=str,
        max_length=20,
        min_length=2,
        pattern="^[A-Z][a-z]*$")
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "user@example.com",
            "password": "pass1234",
            "first_name": "John",
            "last_name": "Smith",
        }
    })


class UpdateAccount(schemas.BaseUserUpdate):
    email: EmailStr = Field(...)
    first_name: str = Field(
        default_factory=str,
        max_length=20,
        min_length=2,
        pattern="^[A-Z][a-z]*$")
    last_name: str = Field(
        default_factory=str,
        max_length=20,
        min_length=2,
        pattern="^[A-Z][a-z]*$")
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "user@example.com",
            "password": "pass1234",
            "first_name": "John",
            "last_name": "Smith",
        }
    })
