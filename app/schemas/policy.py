from typing import Literal, Any
from pydantic import BaseModel, Field
from app.models.documents import ResourceID, Account, Group
from app.utils.permissions import Permissions


class Policy(BaseModel):
    id: ResourceID
    policy_holder_type: Literal["account", "group"]
    policy_holder: Account | Group
    permissions: Permissions


class PolicyShort(BaseModel):
    id: ResourceID
    policy_holder_type: Literal["account", "group"]
    policy_holder: Any


class PolicyInput(BaseModel):
    permissions: list[str] = Field(title="Permissions")

    class Config:
        schema_extra = {
            "example": {
                "permissions": ["get_workspace_info", "list_members"],
            }
        }


# Schema for adding permissions to a group
class AddPermission(BaseModel):
    permissions: list[Permissions] = Field(title="Permissions")

    class Config:
        schema_extra = {
            "example": {
                "permissions": [
                    {
                        "type": "account",
                        "id": "1a2b3c4d5e6f7g8h9i0j",
                        "permission": "eff",
                    },
                    {
                        "type": "account",
                        "id": "2a3b4c5d6e7f8g9h0i1j",
                        "permission": "a3",
                    },
                    {
                        "type": "group",
                        "id": "3a4b5c6d7e8f9g0h1i2j",
                        "permission": "1",
                    },
                ]
            }
        }
