from typing import Literal, Any, Optional
from pydantic import ConfigDict, BaseModel, Field
from unipoll_api.documents import ResourceID, Group, Member


class Policy(BaseModel):
    id: ResourceID
    policy_holder_type: Literal["member", "group"]
    policy_holder: Member | Group
    permissions: int


class PolicyShort(BaseModel):
    id: ResourceID
    policy_holder_type: Literal["member", "group"]
    policy_holder: Any = None
    permissions: Optional[Any] = None


class PolicyInput(BaseModel):
    policy_id: Optional[ResourceID] = Field(None, title="Policy ID")
    account_id: Optional[ResourceID] = Field(None, title="Account ID")
    group_id: Optional[ResourceID] = Field(None, title="Group ID")
    permissions: list[str] = Field(title="Permissions")
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "permissions": ["get_workspace_info", "list_members"],
        }
    })


class PolicyOutput(BaseModel):
    permissions: list[str] = Field(title="List of allowed actions")
    policy_holder: Any = None
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "permissions": [
                "get_workspaces",
                "create_workspace",
                "get_workspace",
                "update_workspace",
                "delete_workspace",
                "get_workspace_members",
                "add_workspace_members",
                "remove_workspace_member",
                "get_groups",
                "create_group",
                "get_all_workspace_policies",
                "get_workspace_policy",
                "set_workspace_policy"
            ],
            "policy_holder": {
                "id": "1a2b3c4d5e6f7g8h9i0j",
                "email": "email@example.com",
                "first_name": "Name",
                "last_name": "Surname",
            }
        }
    })


# Schema for listing all policies in a workspace
class PolicyList(BaseModel):
    policies: list[PolicyShort] = Field(title="Policies")
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "policies": [
                {
                    "permissions": [
                        "get_workspace",
                        "get_groups",
                    ],
                    "policy_holder": {
                            "id": "1a2b3c4d5e6f7g8h9i0j",
                            "email": "email@example.com",
                            "first_name": "Name",
                            "last_name": "Surname",
                    }
                },
                {
                    "permissions": [
                        "get_workspace",
                        "get_groups",
                    ],
                    "policy_holder": {
                            "id": "1a2b3c4d5e6f7g8h9i0j",
                            "email": "email@example.com",
                            "first_name": "Name",
                            "last_name": "Surname",
                    }
                }
            ]
        }
    })


# Schema for adding permissions to a group
class AddPermission(BaseModel):
    permissions: list[str] = Field(title="Permissions")
    model_config = ConfigDict(json_schema_extra={
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
    })


# Schema for returning a list of permissions
class PermissionList(BaseModel):
    permissions: list[str] = Field(title="Permissions")
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "permissions": [
                "get_workspaces",
                "create_workspace",
                "get_workspace",
                "update_workspace",
                "delete_workspace",
                "get_workspace_members",
                "add_workspace_members",
                "remove_workspace_member",
                "get_groups",
                "create_group",
                "get_workspace_policies",
                "get_workspace_policy",
                "set_workspace_policy",
                "get_workspace_permissions"
            ]
        }
    })
