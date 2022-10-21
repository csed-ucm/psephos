from pydantic import BaseModel, Field, EmailStr
from beanie import PydanticObjectId
# from app.models.object_id import PyObjectId 
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase

# class User(BaseModel):
#     id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
#     name: str = Field(...)
#     email: EmailStr = Field(...)
#     password: str = Field(...)

#     class Config:
#         allow_population_by_field_name = True
#         arbitrary_types_allowed = True
#         json_encoders = {ObjectId: str}
#         schema_extra = {
#             "example": {
#                 "name": "Jane Doe",
#                 "email": "jdoe@example.com",
#                 "course": "Experiments, Science, and Fashion in Nanophotonics",
#                 "gpa": "3.0",
#             }
#         }
class User(BeanieBaseUser[PydanticObjectId]):
    pass