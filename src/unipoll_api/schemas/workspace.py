from pydantic import ConfigDict, BaseModel, Field
from typing import Optional
from unipoll_api.documents import ResourceID


# class UpdatableModel(BaseModel):
    
#     @classmethod
#     def add_field(cls, field_name, field_type, default=None):
#         cls.model_fields[field_name] = Field(default=default, title=field_name)
#         cls.model_fields[field_name].default = default
#         cls.model_fields[field_name].annotation = field_type
#         return cls


# Schema for the response with basic workspace info (name and role)
class Workspace(BaseModel):
    id: Optional[ResourceID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    members: Optional[list] = None
    groups: Optional[list] = None
    policies: Optional[list] = None
    polls: Optional[list] = None
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "1a2b3c4d5e6f7g8h9i0j",
            "name": "Workspace 01",
            "description": "This is an example workspace",
        }
    })


class WorkspaceShort(BaseModel):
    id: ResourceID = Field(title="ID")
    name: str = Field(title="Name")
    description: str = Field(title="Description")


# Schema for the response with a list of workspaces
# It can be used to return a list of workspaces with basic info or full info
class WorkspaceList(BaseModel):
    workspaces: list[WorkspaceShort] | list[Workspace]
    model_config = ConfigDict(json_schema_extra={
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
    })


# Schema for the request to create a workspace
class WorkspaceCreateInput(BaseModel):
    name: str = Field(title="Name", description="Name of the resource", min_length=3, max_length=50)
    description: str = Field(default="", title="Description", max_length=1000)
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Workspace 01",
            "description": "This is an example workspace",
        }
    })


# Schema for the request to update a workspace
class WorkspaceUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, title="Name", description="Name of the resource", min_length=3, max_length=50)
    description: Optional[str] = Field(default=None, title="Description", max_length=1000)
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Workspace 01",
            "description": "This is an example workspace",
        }
    })


# Schema for the response when a workspace is created
class WorkspaceCreateOutput(BaseModel):
    id: ResourceID = Field(title="ID")
    name: str = Field(title="Name")
    description: str = Field(title="Description")
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "5eb7cf5a86d9755df3a6c593",
            "name": "Workspace 01",
            "description": "This is an example workspace",
        }
    })
