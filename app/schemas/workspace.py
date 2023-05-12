
# from bson import DBRef
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from app.models.documents import ResourceID
from app.schemas.account import Account
from app.schemas.group import Group
from app.schemas.policy import Policy


# Schema for the response with basic workspace info (name and role)
class Workspace(BaseModel):
    id: Optional[ResourceID]
    name: Optional[str]
    description: Optional[str]
    members: Optional[list]
    groups: Optional[list]
    policies: Optional[list]

    class Config:
        schema_extra = {
            "example": {
                "id": "1a2b3c4d5e6f7g8h9i0j",
                "name": "Workspace 01",
                "description": "This is an example workspace",
            }
        }


class WorkspaceShort(BaseModel):
    id: ResourceID = Field(title="ID")
    name: str = Field(title="Name")
    description: str = Field(title="Description")


# Schema for the response with a list of workspaces
# It can be used to return a list of workspaces with basic info or full info
class WorkspaceList(BaseModel):
    workspaces: List[WorkspaceShort | Workspace]

    class Config:
        schema_extra = {
            "example": {
                "workspaces": [
                    {
                        "name": "Workspace 01",
                        "description": "This is an example workspace",
                        "owner": "true",
                    },
                    {
                        "name": "Workspace 02",
                        "description": "This is another example workspace",
                        "owner": "false",
                    },
                ]
            }
        }


# Schema for the request to create a workspace
class WorkspaceCreateInput(BaseModel):
    name: str = Field(title="Name")
    description: str = Field(title="Description")

    class Config:
        schema_extra = {
            "example": {
                "name": "Workspace 01",
                "description": "This is an example workspace",
            }
        }


# Schema for the response when a workspace is created
class WorkspaceCreateOutput(BaseModel):
    id: ResourceID = Field(title="ID")
    name: str = Field(title="Name")
    description: str = Field(title="Description")

    class Config:
        schema_extra = {
            "example": {
                "name": "Workspace 01",
                "description": "This is an example workspace",
            }
        }


# Temporary schema for the request to add a member to a workspace
class MemberAdd(BaseModel):
    user_id: ResourceID = Field(title="ID")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "1a2b3c4d5e6f7g8h9i0j",
            }
        }


# Schema for the request to add a member to a workspace
class AddMembers(BaseModel):
    accounts: list[ResourceID] = Field(title="Accounts")

    class Config:
        schema_extra = {
            "example": {
                "accounts": [
                    "1a2b3c4d5e6f7g8h9i0j",
                    "2a3b4c5d6e7f8g9h0i1j",
                    "3a4b5c6d7e8f9g0h1i2j"
                ]
            }
        }
