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

    # Add user to group 
    async def add_user(self, user_id: PydanticObjectId, role: str):
        
        # Check if user is already in group
        if user_id in self.users:
            # Return 400 with error message
            raise 
        
        if role == "admin":
            self.admins.append(user_id)
        self.users.append(user_id)
        await self.save()  
    # Remove user from group

    # Delete user from all groups
    # def remove_user(self, user_id: PydanticObjectId):
    #     if user_id in group.users:
    #         group.users.remove(user_id)
    #     if user_id in group.admins:
    #         group.admins.remove(user_id)
    #     group.save()