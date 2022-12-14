from typing import List
from beanie import PydanticObjectId, Document, before_event, after_event, Insert
from pydantic import BaseModel, Field
from app.models.user import User
from devtools import debug

class Group(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    # TODO: Add to documentation about the regex format
    name: str = Field(default="", min_length=3, max_length=50, regex="^[A-Z][A-Za-z]{2,}([ ]([0-9]+|[A-Z][A-Za-z]*))*$")   
    description: str = Field(default="", title="Description", max_length=300)
    owner: PydanticObjectId = Field(default_factory=PydanticObjectId, title="ownerID", description="Owner of the group")
    members:  List[PydanticObjectId] = []
    admins: List[PydanticObjectId] = []

    @after_event(Insert)
    def update_groups(self):
        # self.members.append(self.owner)
        print("Group created", self.name)
        # debug(self.name)