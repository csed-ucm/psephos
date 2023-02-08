from beanie import PydanticObjectId
from pydantic import BaseModel, Field
from typing import List
from app.schemas.user import UserReadShort, UserReadFull


# Custom PydanticObjectId class to override due to a bug
class WorkspaceID(PydanticObjectId):
    @classmethod
    def __modify_schema__(cls, field_schema):  # type: ignore
        field_schema.update(
            type="string",
            example="5eb7cf5a86d9755df3a6c593",
        )


# Schema for the response with basic workspace info (name and role)
class WorkspaceReadShort(BaseModel):
    id: WorkspaceID = Field(title="ID")
    name: str = Field(title="Name")
    description: str = Field(title="Description")
    owner: bool = Field(title="Owner")

    class Config:
        schema_extra = {
            "example": {
                "id": "1a2b3c4d5e6f7g8h9i0j",
                "name": "Workspace 01",
                "description": "This is an example workspace",
                "owner": "true",
            }
        }


# Schema for the response with full workspace info (name, description, owner info)
class WorkspaceReadFull(BaseModel):
    id: WorkspaceID = Field(title="ID")
    name: str = Field(example="Workspace 01", title="Name")
    description: str = Field(title="Description")
    owner: UserReadShort = Field(title="Owner")
    members_count: int = Field(title="Members count")

    class Config:
        schema_extra = {
            "example":         {
                "name": "Workspace 01",
                "description": "This is an example workspace",
                "owner": {
                    "id": "1a2b3c4d5e6f7g8h9i0j",
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Smith"
                },
                "members_count": 34
            }
        }


# Schema for the response with a list of workspaces
# It can be used to return a list of workspaces with basic info or full info
class WorkspaceList(BaseModel):
    workspaces: List[WorkspaceReadShort | WorkspaceReadFull]

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
    id: WorkspaceID = Field(...)
    name: str = Field(title="Name")
    description: str = Field(title="Description")
    owner: UserReadShort = Field(title="Owner")

    class Config:
        schema_extra = {
            "example": {
                "name": "Workspace 01",
                "description": "This is an example workspace",
            }
        }
