from beanie import PydanticObjectId
from pydantic import BaseModel, Field
from typing import List
from random import choice, randint
from fastapi import Response
from app.models.group import Group
from app.models.user import User
from app.schemas.user import UserAddToGroup


class GroupList(BaseModel):
    groups: List[Group]


class GroupRead(BaseModel):
    name: str
    description: str
    owner_name: str
    owner_email: str

            
class GroupCreateIn(BaseModel):
    name: str = Field(default="", min_length=3, max_length=50, regex="^[A-Z][A-Za-z]{2,}([ ]([0-9]+|[A-Z][A-Za-z]*))*$")
    description: str = Field(default="", title="Description", max_length=300)
    class Config:
        schema_extra = {
            "example": {
                "name": "Group 01",
                "description": "My first Group",
            }
        }
    
class GroupCreateOut(BaseModel):
    message: str = "Group created successfully"
    name: str
    # description: str
    
class GroupUpdateIn(BaseModel):
    name: str = Field(default="", min_length=3, max_length=50, regex="^[A-Z][A-Za-z]{2,}([ ]([0-9]+|[A-Z][A-Za-z]*))*$")
    description: str = Field(default="", title="Description", max_length=300)

class GroupUpdateOut(Response):
    status_code = 200
    media_type = "application/json"
    content = {"message": "Group updated successfully"} 

class GroupAddMembers(BaseModel):
    members: List[UserAddToGroup]
    class Config:
        schema_extra = {
            "example": {
                "members": [
                    {"email": "user1@example.com", "role": "admin"},
                    {"email": "user2@example.com", "role": "user"},
                ]
            }
        }
    

class GroupReadMembers(BaseModel):
    members: List[User]