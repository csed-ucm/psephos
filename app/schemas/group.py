from pydantic import BaseModel, Field, EmailStr
from typing import Any, List, Optional
from app.models.documents import ResourceID
from app.utils.permissions import Permissions


class Group(BaseModel):
    id: Optional[ResourceID]
    name: Optional[str]
    description: Optional[str]
    workspace: Optional[Any]
    groups: Optional[list]
    members: Optional[list]
    policies: Optional[list]


class GroupShort(BaseModel):
    id: ResourceID
    name: str
    description: str


# Schema for the response with basic group info
class GroupList(BaseModel):
    groups: list[GroupShort] | list[Group]


# Schema for the request to create a new group
class GroupCreateInput(BaseModel):
    name: str = Field(
        default="",
        min_length=3,
        max_length=50,
        regex="^[A-Z][A-Za-z]{2,}([ ]([0-9]+|[A-Z][A-Za-z]*))*$")
    description: str = Field(default="", title="Description", max_length=300)

    class Config:
        schema_extra = {
            "example": {
                "name": "Group 01",
                "description": "My first Group",
            }
        }


# Schema for the response to a group creation request
class GroupCreateOutput(BaseModel):
    id: ResourceID
    name: str
    description: str


# Schema for the request to add a user to a group
class GroupUpdateIn(BaseModel):
    name: Optional[str] = Field(
        default="",
        min_length=3,
        max_length=50,
        regex="^[A-Z][A-Za-z]{2,}([ ]([0-9]+|[A-Z][A-Za-z]*))*$")
    description: Optional[str] = Field(default="", title="Description", max_length=300)

    class Config:
        schema_extra = {
            "example": {
                "Description": "Updated description"
            }
        }


# Schema for the response with basic member info
class GroupMember(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: str = Field(default="user", title="Role")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "user",
            }
        }


# Temporary schema for the request to add a member to a workspace
class AddMembers(BaseModel):
    accounts: list[ResourceID]
    # groups: list[ResourceID]

    class Config:
        schema_extra = {
            "example": {
                "accounts": [
                    "1a2b3c4d5e6f7g8h9i0j",
                    "2a3b4c5d6e7f8g9h0i1j",
                    "3a4b5c6d7e8f9g0h1i2j"
                ],
                # "groups": [
                #     "4a5b6c7d8e9f0g1h2i3j",
                #     "5a6b7c8d9e0f1g2h3i4j",
                #     "6a7b8c9d0e1f2g3h4i5j"
                # ]
            }
        }


# Schema for the response with a list of members and their info
class GroupReadMembers(BaseModel):
    members: List[GroupMember]

    class Config:
        schema_extra = {
            "example": {
                "members": [
                    {
                        "email": "jdoe@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "role": "admin"
                    },
                    {
                        "email": "jsmith@example.com",
                        "first_name": "Jack",
                        "last_name": "Smith",
                        "role": "user"
                    }
                ]
            }
        }
