from typing import List
from beanie import PydanticObjectId, Document
from pydantic import BaseModel, Field
from app.models.user import User

class Group(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    name: str = Field(default="", min_length=3, max_length=50, regex=r'^[A-Z][A-Za-z]{2,}(\s(\d+|[A-Z][A-Za-z]*))*$')   
    description: str = Field(default="", title="Description", max_length=300)
    owner: PydanticObjectId = Field(default_factory=PydanticObjectId, title="ownerID", description="Owner of the group")
    users:  List[PydanticObjectId] = []
    admins: List[PydanticObjectId] = []