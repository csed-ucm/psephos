from pydantic import ConfigDict, BaseModel, Field
from typing import Any, Optional
from unipoll_api.documents import ResourceID


class Group(BaseModel):
    id: Optional[ResourceID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    workspace: Optional[Any] = None
    # groups: Optional[list]
    members: Optional[list] = None
    policies: Optional[list] = None


# Schema for the response with basic group info after creation
class GroupShort(BaseModel):
    id: ResourceID
    name: str
    description: str


# Schema for the response with basic group info
class GroupList(BaseModel):
    groups: list[GroupShort] | list[Group]


# Schema for the request to create a new group
class GroupCreateRequest(BaseModel):
    name: str = Field(default="", min_length=3, max_length=50)
    workspace: ResourceID = Field(title="Workspace ID")
    description: str = Field(default="", title="Description", max_length=300)
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Group 01",
            "workspace": "60b9d1c8e1f1d5f5f5b4f8e1",
            "description": "My first Group",
        }
    })


# Schema for the request to create a new group
class GroupCreateInput(BaseModel):
    name: str = Field(default="", min_length=3, max_length=50)
    description: str = Field(default="", title="Description", max_length=300)
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Group 01",
            "description": "My first Group",
        }
    })


# Schema for the response to a group creation request
class GroupCreateOutput(BaseModel):
    id: ResourceID
    name: str
    description: str


# Schema for the request to add a user to a group
class GroupUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, title="Name", min_length=3, max_length=50)
    description: Optional[str] = Field(default="", title="Description", max_length=300)
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "Description": "Updated description"
        }
    })
