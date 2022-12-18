from fastapi import HTTPException
# from fastapi.logger import logger
from beanie import PydanticObjectId
# from pydantic import EmailStr, Field
# from app.models.user import User
# from app.models.group import Group
from app.utils.colored_dbg import print_warning


class UserNotFound(HTTPException):
    def __init__(self, user: PydanticObjectId | str | None = None):
        message = "User not found"  # Default message
        if user:
            if user.__class__ == PydanticObjectId:
                message = f"User with id {user} not found"
            elif user.__class__ == str:
                message = f"User with email {user} not found"
            # elif user.__class__ == str:
            #     message = f"User with name {user} not found"
        super().__init__(status_code=404, detail=message)

    def __str__(self) -> str:
        # logger.warning(self.detail)
        print_warning(self.detail)
        return self.detail
