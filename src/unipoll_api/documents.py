# from typing import ForwardRef, NewType, TypeAlias, Optional
from typing import Literal
from bson import DBRef
from beanie import Document, WriteRules, after_event, Insert, Link, PydanticObjectId  # BackLink
from fastapi_users_db_beanie import BeanieBaseUser
from pydantic import Field
from unipoll_api.utils import colored_dbg as Debug
from unipoll_api.utils.permissions import Permissions  # WorkspacePermissions
from unipoll_api.utils.token_db import BeanieBaseAccessToken


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


class AccessToken(BeanieBaseAccessToken, Document):  # type: ignore
    pass


class Resource(Document):
    id: ResourceID = Field(default_factory=ResourceID, alias="_id")
    resource_type = ""
    name: str = Field(title="Name", description="Name of the resource", min_length=3, max_length=50)
    # Field(default="", min_length=3, max_length=50, regex="^[A-Z][A-Za-z]{2,}([ ]([0-9]+|[A-Z][A-Za-z]*))*$")
    description: str = Field(default="", title="Description", max_length=1000)
    policies: list[Link["Policy"]] = []
    # If the resource is a root resource, all derived resources will be stored in the same collection
    # However, the benefits of this are unclear
    # class Settings:
    #     is_root = True

    @after_event(Insert)
    def create_group(self) -> None:
        Debug.info(f'New {self.resource_type} "{self.id}" has been created')

    async def add_member(self, workspace, account: "Account", permissions, save: bool = True) -> "Account":
        # Add the account to the group
        self.members.append(account)  # type: ignore
        # Create a policy for the new member
        new_policy = Policy(policy_holder_type='account',
                            policy_holder=(await create_link(account)),
                            permissions=permissions,
                            workspace=workspace)

        # Add the policy to the group
        self.policies.append(new_policy)  # type: ignore
        if save:
            await Resource.save(self, link_rule=WriteRules.WRITE)
        return account

    async def remove_member(self, account, save: bool = True) -> bool:
        # Remove the account from the group
        # await self.fetch_link("members")
        for i, member in enumerate(self.members):
            if account.id == member.id:  # type: ignore
                self.members.remove(member)
                Debug.info(f"Removed member {member.id} from {self.resource_type} {self.id}")  # type: ignore
                break

        # Remove the policy from the group
        # await self.fetch_link("policies")
        for policy in self.policies:
            # pc = await policy.policy_holder.fetch()  # type: ignore
            pc = policy.policy_holder  # type: ignore
            if pc.ref.id == account.id:
                self.policies.remove(policy)
                await Policy.delete(policy)
                Debug.info(f"Removed policy: {pc.ref.id} from {self.resource_type} {self.id}")
                break

        await self.save(link_rule=WriteRules.WRITE)  # type: ignore
        return True


class Account(BeanieBaseUser, Document):  # type: ignore
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
    members: list[Link["Account"]] = []
    groups: list[Link["Group"]] = []
    polls: list[Link["Poll"]] = []


class Group(Resource):
    resource_type = "group"
    workspace: Link["Workspace"]
    # workspace: list[BackLink[Workspace]] = Field(original_field="groups")
    members: list[Link["Account"]] = []
    groups: list[Link["Group"]] = []


class Policy(Document):
    id: ResourceID = Field(default_factory=ResourceID, alias="_id")
    workspace: Link["Workspace"]
    # workspace: BackLink[Workspace] = Field(original_field="policies")
    policy_holder_type: Literal["account", "group"]
    policy_holder: Link["Group"] | Link["Account"]
    # policy_holder: list[Link["Account"]]
    # policy_holder: Link[Resource]
    permissions: Permissions


class Poll(Resource):
    id: ResourceID = Field(default_factory=ResourceID, alias="_id")
    workspace: Link["Workspace"]
    resource_type = "poll"
    public: bool
    published: bool
    questions: list
    policies: list[Link["Policy"]]


# NOTE: ForwardRef is used to avoid circular imports
Resource.update_forward_refs()
Workspace.update_forward_refs()
Group.update_forward_refs()
Policy.update_forward_refs()
Poll.update_forward_refs()
# Question.update_forward_refs()
