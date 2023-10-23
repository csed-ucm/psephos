# from typing import ForwardRef, NewType, TypeAlias, Optional
from typing import Literal
from bson import DBRef
from beanie import Document as BeanieDocument
from beanie import BackLink, WriteRules, after_event, Insert, Link, PydanticObjectId  # BackLink
from fastapi_users_db_beanie import BeanieBaseUser
from pydantic import Field
from unipoll_api.utils import colored_dbg as Debug
from unipoll_api.utils.token_db import BeanieBaseAccessToken


# Document
class Document(BeanieDocument):
    @classmethod
    def get_document_type(cls) -> str:
        return cls._document_settings.name  # type: ignore


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
    name: str = Field(
        title="Name", description="Name of the resource", min_length=3, max_length=50)
    description: str = Field(default="", title="Description", max_length=1000)
    policies: list[Link["Policy"]] = []

    @after_event(Insert)
    def create_group(self) -> None:
        Debug.info(f'New {self.get_document_type()} "{self.id}" has been created')

    async def add_policy(self, member: "Group | Member", permissions, save: bool = True) -> "Policy":
        new_policy = Policy(policy_holder_type='member',
                            policy_holder=(await create_link(member)),
                            permissions=permissions,
                            parent_resource=(await create_link(self)))  # type: ignore

        # Add the policy to the group
        self.policies.append(new_policy)  # type: ignore
        if save:
            await self.save(link_rule=WriteRules.WRITE)  # type: ignore
        return new_policy

    async def remove_policy(self, policy: "Policy", save: bool = True) -> None:
        for i, p in enumerate(self.policies):
            if policy.id == p.ref.id:
                self.policies.remove(p)
                if save:
                    await self.save(link_rule=WriteRules.WRITE)  # type: ignore

    async def remove_policy_by_holder(self, policy_holder: "Group | Member", save: bool = True) -> None:
        for policy in self.policies:
            if policy.policy_holder.ref.id == policy_holder.id:  # type: ignore
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
    members: list[Link["Member"]] = []
    groups: list[Link["Group"]] = []
    polls: list[Link["Poll"]] = []

    async def add_member(self, account: "Account", permissions, save: bool = True) -> "Member":
        new_member = await Member(account=account, resource=(await create_link(self))).create()  # type: ignore
        new_policy = await self.add_policy(new_member, permissions, save=False)  # type: ignore
        new_member.policies.append(new_policy)  # type: ignore

        self.members.append(new_member)  # type: ignore

        if save:
            await self.save(link_rule=WriteRules.WRITE)  # type: ignore
        return new_member

    async def remove_member(self, member_to_delete: "Member", save: bool = True) -> bool:
        # Remove the account from the workspace
        for member in self.members:
            if member.id == member_to_delete.id:  # type: ignore
                self.members.remove(member)
                await member.delete()  # type: ignore
                # type: ignore
                Debug.info(f"Removed member {member.id} from {self.get_document_type()} {self.id}")  # type: ignore
                break

        # Remove the policy from the workspace
        await self.remove_policy_by_holder(member_to_delete, save=False)  # type: ignore

        # Remove the member from all groups in the workspace
        group: Group
        for group in self.groups:  # type: ignore
            await group.remove_member(member_to_delete, save=False)
            await group.remove_policy_by_holder(member_to_delete, save=False)
            await Group.save(group, link_rule=WriteRules.WRITE)

        if save:
            await self.save(link_rule=WriteRules.WRITE)  # type: ignore
        return True


class Group(Resource):
    workspace: BackLink[Workspace] = Field(original_field="groups")
    members: list[Link["Member"]] = []
    groups: list[Link["Group"]] = []

    async def add_member(self, member: "Member", permissions, save: bool = True) -> "Member":
        if member.workspace.id != self.workspace.id:  # type: ignore
            from unipoll_api.exceptions import WorkspaceExceptions
            raise WorkspaceExceptions.UserNotMember(
                self.workspace, member)  # type: ignore

        # Add the member to the group's list of members
        self.members.append(member)  # type: ignore
        # Create a policy for the new member
        await self.add_policy(member, permissions, save=False)  # type: ignore
        if save:
            await self.save(link_rule=WriteRules.WRITE)  # type: ignore
        return member

    async def remove_member(self, member: "Member", save: bool = True) -> bool:
        # Remove the account from the group
        for _member in self.members:
            if _member.id == member.id:  # type: ignore
                self.members.remove(_member)
                # type: ignore
                Debug.info(
                    f"Removed member {member.id} from {self.get_document_type()} {self.id}")  # type: ignore
                break

        # Remove the policy from the group
        await self.remove_policy_by_holder(member, save=False)  # type: ignore

        if save:
            await self.save(link_rule=WriteRules.WRITE)  # type: ignore
        return True


class Poll(Resource):
    id: ResourceID = Field(default_factory=ResourceID, alias="_id")
    workspace: Link[Workspace]
    public: bool
    published: bool
    questions: list
    policies: list[Link["Policy"]]


class Policy(Document):
    id: ResourceID = Field(default_factory=ResourceID, alias="_id")
    parent_resource: Link[Workspace] | Link[Group] | Link[Poll]
    policy_holder_type: Literal["member", "group"]
    policy_holder: Link["Group"] | Link["Member"]
    permissions: int

    async def get_parent_resource(self, fetch_links: bool = False) -> Workspace | Group | Poll:
        from unipoll_api.exceptions.resource import ResourceNotFound
        collection = eval(self.parent_resource.ref.collection)
        parent: Workspace | Group | Poll = await collection.get(self.parent_resource.ref.id,
                                                                fetch_links=fetch_links)
        if not parent:
            ResourceNotFound(self.parent_resource.ref.collection,
                             self.parent_resource.ref.id)
        return parent

    async def get_policy_holder(self, fetch_links: bool = False) -> "Group | Member":
        from unipoll_api.exceptions.policy import PolicyHolderNotFound
        collection = eval(self.policy_holder.ref.collection)
        policy_holder: Group | Member = await collection.get(self.policy_holder.ref.id,
                                                             fetch_links=fetch_links)
        if not policy_holder:
            PolicyHolderNotFound(self.policy_holder.ref.id)
        return policy_holder


class Member(Document):
    id: ResourceID = Field(default_factory=ResourceID, alias="_id")
    account: Link[Account]
    workspace: BackLink[Workspace] = Field(original_field="members")
    groups: list[BackLink[Group]] = Field(original_field="members")
    policies: list[Link[Policy]] = []
