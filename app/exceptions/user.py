from fastapi import HTTPException
from beanie import PydanticObjectId
from app.models.user import User
from app.models.group import Group
from app.utils.colored_dbg import print_warning


class UserNotFound(HTTPException):
    def __init__(self, user_id: PydanticObjectId):
        super().__init__(status_code=404, detail=f"User with id {user_id} not found") 

    def __str__(self):
        print_warning(self.detail)