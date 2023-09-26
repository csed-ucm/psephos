from fastapi import status
from unipoll_api.documents import Account, Resource, ResourceID
from unipoll_api.utils import Debug


class APIException(Exception):
    def __init__(self, code: int, detail: str):
        self.code = code
        self.detail = detail

    def __str__(self) -> str:
        Debug.print_error(self.detail)  # type: ignore
        return self.detail


class InternalServerError(APIException):
    def __init__(self, detail: str):
        super().__init__(code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail="Internal Server Error")
        Debug.print_error(detail)  # type: ignore


class NonUniqueName(APIException):
    def __init__(self, resource: str, resource_name: str):
        super().__init__(code=status.HTTP_400_BAD_REQUEST,
                         detail=f"{resource} with name {resource_name} already exists")


class ErrorWhileCreating(APIException):
    def __init__(self, resource: str, resource_name: str):
        super().__init__(code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail=f"Error while creating {resource} {resource_name}")


class ResourceNotFound(APIException):
    def __init__(self, resource: str, resource_id: ResourceID):
        super().__init__(code=status.HTTP_404_NOT_FOUND,
                         detail=f"{resource} #{resource_id} does not exist")


class ErrorWhileDeleting(APIException):
    def __init__(self, resource: str, resource_id: ResourceID):
        super().__init__(code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail=f"Error while deleting {resource} #{resource_id}")


# Not authorized
class UserNotAuthorized(APIException):
    def __init__(self, account: Account, resource: str, action: str = "perform this action"):
        super().__init__(code=status.HTTP_403_FORBIDDEN,
                         detail=f"User {account.email} is not authorized to {action} in {resource}")


# Action not found
class ActionNotFound(APIException):
    def __init__(self, resource: str, action: str):
        super().__init__(code=status.HTTP_400_BAD_REQUEST,
                         detail=f"Action {action} not found in {resource}")


# Invalid permission
class InvalidPermission(APIException):
    def __init__(self, permission: str):
        super().__init__(code=status.HTTP_400_BAD_REQUEST,
                         detail=f"Invalid permission {permission}")


# User not a member of resource
class UserNotMember(APIException):
    def __init__(self, resource: Resource, user: Account):
        super().__init__(code=status.HTTP_400_BAD_REQUEST,
                         detail=f"User {user.email} is not a member of {resource.name} #{resource.id}")


# User already a member of resource
class AddingExistingMember(APIException):
    def __init__(self, resource: Resource, user: Account):
        super().__init__(code=status.HTTP_400_BAD_REQUEST,
                         detail=f"User {user.email} is already a member of {resource.name} #{resource.id}")


# Error while removing member
class ErrorWhileRemovingMember(APIException):
    def __init__(self, resource: Resource, user: Account):
        super().__init__(code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail=f"Error while removing user {user.email} from {resource.name} #{resource.id}")
