# from typing import ForwardRef, NewType, TypeAlias, Optional
from typing import Literal
from bson import DBRef
from beanie import BackLink, Document, WriteRules, after_event, Insert, Link, PydanticObjectId  # BackLink
from fastapi_users_db_beanie import BeanieBaseUser
from pydantic import Field
from unipoll_api.utils import colored_dbg as Debug
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
    resource_type: Literal["workspace", "group", "poll"]
    name: str = Field(title="Name", description="Name of the resource", min_length=3, max_length=50)
    description: str = Field(default="", title="Description", max_length=1000)
    policies: list[Link["Policy"]] = []

    @after_event(Insert)
    def create_group(self) -> None:
        Debug.info(f'New {self.resource_type} "{self.id}" has been created')

    async def add_policy(self, member: "Group | Account", permissions, save: bool = True) -> None:
        new_policy = Policy(policy_holder_type='account',
                            policy_holder=(await create_link(member)),
                            permissions=permissions,
                            parent_resource=self)  # type: ignore

        # Add the policy to the group
        self.policies.append(new_policy)  # type: ignore
        if save:
            await self.save(link_rule=WriteRules.WRITE)  # type: ignore

    async def remove_policy(self, member: "Group | Account", save: bool = True) -> None:
        for policy in self.policies:
            if policy.policy_holder.id == member.id:  # type: ignore
                self.policies.remove(policy)
                if save:
                    await self.save(link_rule=WriteRules.WRITE)  # type: ignore


class Account(BeanieBaseUser, Document):  # type: ignore
    id: ResourceID = Field(default_factory=ResourceID, alias="_id")
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


class Workspace(Resource):
    resource_type: Literal["workspace"] = "workspace"
    members: list[Link["Account"]] = []
    groups: list[Link["Group"]] = []
    polls: list[Link["Poll"]] = []

    async def add_member(self, account: "Account", permissions, save: bool = True) -> "Account":
        # Add the account to the group
        self.members.append(account)  # type: ignore
        # Create a policy for the new member
        await self.add_policy(account, permissions, save=False)  # type: ignore
        if save:
            await self.save(link_rule=WriteRules.WRITE)  # type: ignore
        return account

    async def remove_member(self, account, save: bool = True) -> bool:
        # Remove the account from the group
        for i, member in enumerate(self.members):
            if account.id == member.id:  # type: ignore
                self.members.remove(member)
                Debug.info(f"Removed member {member.id} from {self.resource_type} {self.id}")  # type: ignore
                break

        # Remove the policy from the workspace
        await self.remove_policy(account, save=False)  # type: ignore

        # Remove the member from all groups in the workspace
        group: Group
        for group in self.groups:  # type: ignore
            await group.remove_member(account, save=False)
            await group.remove_policy(account, save=False)
            await Group.save(group, link_rule=WriteRules.WRITE)

        if save:
            await self.save(link_rule=WriteRules.WRITE)  # type: ignore
        return True


class Group(Resource):
    resource_type: Literal["group"] = "group"
    workspace: BackLink[Workspace] = Field(original_field="groups")
    members: list[Link["Account"]] = []
    groups: list[Link["Group"]] = []

    async def add_member(self, account: "Account", permissions, save: bool = True) -> "Account":
        if account not in self.workspace.members:  # type: ignore
            from unipoll_api.exceptions import WorkspaceExceptions
            raise WorkspaceExceptions.UserNotMember(self.workspace, account)  # type: ignore

        # Add the account to the group
        self.members.append(account)  # type: ignore
        # Create a policy for the new member
        await self.add_policy(account, permissions, save=False)  # type: ignore
        if save:
            await self.save(link_rule=WriteRules.WRITE)  # type: ignore
        return account

    async def remove_member(self, account, save: bool = True) -> bool:
        # Remove the account from the group
        for i, member in enumerate(self.members):
            if account.id == member.id:  # type: ignore
                self.members.remove(member)
                Debug.info(f"Removed member {member.id} from {self.resource_type} {self.id}")  # type: ignore
                break

        # Remove the policy from the group
        await self.remove_policy(account, save=False)  # type: ignore

        if save:
            await self.save(link_rule=WriteRules.WRITE)  # type: ignore
        return True


class Policy(Document):
    id: ResourceID = Field(default_factory=ResourceID, alias="_id")
    parent_resource: BackLink["Workspace"] | BackLink["Group"] | BackLink["Poll"] = Field(original_field="policies")
    policy_holder_type: Literal["account", "group"]
    policy_holder: Link["Group"] | Link["Account"]
    permissions: int


class Poll(Resource):
    id: ResourceID = Field(default_factory=ResourceID, alias="_id")
    workspace: BackLink["Workspace"] = Field(original_field="polls")
    resource_type: Literal["poll"] = "poll"
    public: bool
    published: bool
    questions: list
    policies: list[Link["Policy"]]


# NOTE: model_rebuild is used to avoid circular imports
Resource.model_rebuild()
Workspace.model_rebuild()
Group.model_rebuild()
Policy.model_rebuild()
Poll.model_rebuild()
