from typing import List
from beanie import Document, after_event, Insert
from pydantic import Field
from app.utils import colored_dbg
from app.schemas.group import GroupID
from app.schemas.user import UserID


class Group(Document):
    id: GroupID = Field(default_factory=GroupID, alias="_id")
    # TODO: Add to documentation about the regex format
    name: str = Field(default="", min_length=3, max_length=50,
                      regex="^[A-Z][A-Za-z]{2,}([ ]([0-9]+|[A-Z][A-Za-z]*))*$")
    description: str = Field(default="", title="Description", max_length=300)
    owner: UserID = Field(
        default_factory=UserID, title="ownerID",
        description="Owner of the group")
    members: List[UserID] = []
    admins: List[UserID] = []

    @after_event(Insert)
    def create_group(self) -> None:
        # self.members.append(self.owner)
        colored_dbg.info(f'New group "{self.id}" has been created')
