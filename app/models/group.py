from typing import List
from beanie import PydanticObjectId
from pydantic import BaseModel, Field
from app.models.user import User

class Group():
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    users:  List[PydanticObjectId] = []
    admins: List[PydanticObjectId] = []
    owner:  User