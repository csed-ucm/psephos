from beanie import PydanticObjectId
from app.models.group import Group
from pydantic import BaseModel, Field
from typing import List
from random import choice, randint

class GroupList(BaseModel):
    groups: List[Group]


class GroupRead(BaseModel):
    name: str
    description: str
    owner: str

    class Config:
            schema_extra = {
                "example": {
                    "name": "Foo",
                    "description": "A very nice Group"
                }
            }
            
class GroupCreate(BaseModel):
    name: str = Field(default="", min_length=3, max_length=50, regex=r'^[A-Z][A-Za-z]{2,}(\s(\d+|[A-Z][A-Za-z]*))*$')
    description: str = Field(default="", title="Description", max_length=300)
    
# class groupUpdate(BaseModel):
#     name: str
#     description: str

