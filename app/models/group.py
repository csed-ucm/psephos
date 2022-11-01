from typing import List
from beanie import PydanticObjectId, Document
from pydantic import BaseModel, Field
from app.models.user import User

class Group(Document):
    # id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    name: str = Field(...)
    # owner: User = Field(...)
    owner: PydanticObjectId = Field(...)
    users:  List[PydanticObjectId] = []
    admins: List[PydanticObjectId] = []