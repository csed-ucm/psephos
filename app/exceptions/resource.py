from fastapi import HTTPException, status
from app.models.documents import Account, Resource
from app.utils.colored_dbg import print_warning
from beanie import PydanticObjectId


class NonUniqueName(HTTPException):
    def __init__(self, resource: str, resource_name: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"{resource} with name \"{resource_name}\" already exists")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
        # logger.warning(self.detail)


class ErrorWhileCreating(HTTPException):
    def __init__(self, resource: str, resource_name: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail=f"Error while creating {resource} {resource_name}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
        # logger.warning(self.detail)


class ResourceNotFound(HTTPException):
    def __init__(self, resource: str, resource_id: PydanticObjectId):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"{resource} #{resource_id} does not exist")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
        # logger.warning(self.detail)


class ErrorWhileDeleting(HTTPException):
    def __init__(self, resource: str, resource_id: PydanticObjectId):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail=f"Error while deleting {resource} #{resource_id}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
        # logger.warning(self.detail)


# Not authorized
class UserNotAuthorized(HTTPException):
    def __init__(self, account: Account, resource: str, action: str = "perform this action"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN,
                         detail=f"User {account.email} is not authorized to {action} in {resource}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail


# Action not found
class ActionNotFound(HTTPException):
    def __init__(self, resource: str, action: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"Action {action} not found in {resource}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail


# Invalid permission
class InvalidPermission(HTTPException):
    def __init__(self, permission: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"Invalid permission {permission}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail


# User not a member of resource
class UserNotMember(HTTPException):
    def __init__(self, resource: Resource, user: Account):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"User {user.email} is not a member of {resource.name} #{resource.id}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
