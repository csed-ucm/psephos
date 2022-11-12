# File to store all the custom exceptions

from fastapi import HTTPException
from beanie import PydanticObjectId
from app.models.user import User
from app.models.group import Group
from app.utils.colored_dbg import print_warning

# If user already exists in the group
class user_exists(HTTPException):
    def __init__(self, user: User, group: Group):
        super().__init__(status_code=400, detail=f"User {user.email} already exists in group {group.name}") 

    def __str__(self):
        print_warning(self.detail)
        # return self.P

# Not authorized
class user_not_authorized(HTTPException):
    def __init__(self, user: User, group: Group, action: str = "perform this action"):
        super().__init__(status_code=403, detail=f"User {user.email} is not authorized to {action} in group {group.name}") 

    def __str__(self):
        print_warning(self.detail)