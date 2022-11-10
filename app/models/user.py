# from pydantic import BaseModel, Field, EmailStr
# from tokenize import group
from typing import List, Dict
from beanie import PydanticObjectId
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase

class User(BeanieBaseUser[PydanticObjectId]):
    # groups: Dict[List[PydanticObjectId], str] = {}
    groups: List[PydanticObjectId] = []

