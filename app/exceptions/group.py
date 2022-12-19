# File to store all the custom exceptions

from fastapi import HTTPException, status
# from fastapi.logger import logger
from beanie import PydanticObjectId
from app.models.user import User
from app.models.group import Group
from app.utils.colored_dbg import print_warning

# If user already exists in the group


class UserAlreadyExists(HTTPException):
    def __init__(self, user: User, group: Group):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"User {user.email} already exists in group {group.name}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
        # logger.warning(self.detail)

# User not in the group


class UserNotInGroup(HTTPException):
    def __init__(self, user: User, group: Group):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"User {user.email} not in group {group.name}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
        # return self.P
        # logger.warning(self.detail)

# Not authorized


class UserNotAuthorized(HTTPException):
    def __init__(
            self,
            user: User,
            group: Group,
            action: str = "perform this action in"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN,
                         detail=f"User {user.email} is not authorized to {action} group {group.name}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail

# Group not found


class GroupNotFound(HTTPException):
    def __init__(self, group_id: PydanticObjectId):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
