# from typing import ForwardRef, NewType, TypeAlias, Optional
from typing import Literal
from bson import DBRef
# from typing import ForwardRef, Optional
from beanie import Document, WriteRules, after_event, Insert, Link, PydanticObjectId, BackLink
from fastapi_users_db_beanie import BeanieBaseUser
from pydantic import Field
from app.utils import colored_dbg
from app.utils.permissions import Permissions, WorkspacePermissions


# Create a link to the Document model
async def create_link(document: Document) -> Link:
    ref = DBRef(collection=document._document_settings.name,  # type: ignore
                id=document.id)
    link = Link(ref, type(document))
    return link


# Custom PydanticObjectId class to override due to a bug
class ResourceID(PydanticObjectId):
    @classmethod
    def __modify_schema__(cls, field_schema):  # type: ignore
        field_schema.update(
            type="string",
            example="5eb7cf5a86d9755df3a6c593",
        )


class Resource(Document):
    id: ResourceID = Field(default_factory=ResourceID, alias="_id")
    resource_type = ""
    name: str = Field(title="Name", description="Name of the resource", min_length=3, max_length=50)
    # Field(default="", min_length=3, max_length=50, regex="^[A-Z][A-Za-z]{2,}([ ]([0-9]+|[A-Z][A-Za-z]*))*$")
    description: str = Field(default="", title="Description", max_length=300)
    members: list[Link["Account"]] = []
    groups: list[Link["Group"]] = []
    policies: list[Link["Policy"]] = []

    # If the resource is a root resource, all derived resources will be stored in the same collection
    # However, the benefits of this are unclear
    # class Settings:
    #     is_root = True

    @after_event(Insert)
    def create_group(self) -> None:
        colored_dbg.info(f'New {self.resource_type} "{self.id}" has been created')

    async def add_member(self, workspace, account, permissions, save: bool = True) -> "Account":
        # Add the account to the group
        self.members.append(account)
        # Create a policy for the new member
        new_policy = Policy(policy_holder_type='account',
                            policy_holder=(await create_link(account)),
                            permissions=permissions,
                            workspace=workspace)

        # Add the policy to the group
        self.policies.append(new_policy)
        if save:
            await Resource.save(self, link_rule=WriteRules.WRITE)
        return account


class Account(BeanieBaseUser, Document):
    id: ResourceID = Field(default_factory=ResourceID, alias="_id")
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


class Workspace(Resource):
    resource_type = "workspace"


class Group(Resource):
    resource_type = "group"
    workspace: Link["Workspace"]
    # workspace: list[BackLink[Workspace]] = Field(original_field="groups")


class Policy(Document):
    id: ResourceID = Field(default_factory=ResourceID, alias="_id")
    workspace: Link["Workspace"]
    # workspace: BackLink[Workspace] = Field(original_field="policies")
    policy_holder_type: Literal["account", "group"]
    policy_holder: Link["Group"] | Link["Account"]
    # policy_holder: list[Link["Account"]]
    # policy_holder: Link[Resource]
    permissions: Permissions


# NOTE: ForwardRef is used to avoid circular imports
Resource.update_forward_refs()
Workspace.update_forward_refs()
Group.update_forward_refs()
Policy.update_forward_refs()
