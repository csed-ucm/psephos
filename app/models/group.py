# from typing import ForwardRef, NewType, TypeAlias, Optional
from beanie import Document, after_event, Insert, Link
from pydantic import Field
from app.schemas.workspace import WorkspaceID
from app.utils import colored_dbg
from app.models.user import User
from app.schemas.group import GroupID
from app.mongo_db import create_link


class Group(Document):
    id: GroupID = Field(default_factory=GroupID, alias="_id")
    # TODO: Add to documentation about the regex format
    name: str = Field(default="", min_length=3, max_length=50,
                      regex="^[A-Z][A-Za-z]{2,}([ ]([0-9]+|[A-Z][A-Za-z]*))*$")
    description: str = Field(default="", title="Description", max_length=300)
    # workspace: Link["Workspace"] = Field(title="Workspace", description="Workspace of the group")
    workspace: WorkspaceID
    owner: Link[User] = Field(title="Owner", description="Owner of the group")
    members: list[Link[User]] = []

    @after_event(Insert)
    def create_group(self) -> None:
        colored_dbg.info(f'New group "{self.id}" has been created')

    async def add_member(self, user: User) -> None:
        link = await create_link(user)
        self.members.append(link)
        colored_dbg.info(
            f'User {user.id} has been added to Group {self.id} as a member.')
        await Group.save(self)
