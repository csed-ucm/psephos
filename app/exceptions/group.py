# File to store all the custom exceptions
from fastapi import HTTPException, status
from app.models.documents import ResourceID, Account, Group
from app.utils.colored_dbg import print_warning
from app.exceptions import resource


# Exception for when a Group with the same name already exists
class NonUniqueName(resource.NonUniqueName):
    def __init__(self, group: Group):
        super().__init__("Group", resource_name=group.name)


# Exception for when an error occurs during Group creation
class ErrorWhileCreating(resource.ErrorWhileCreating):
    def __init__(self, group: Group):
        super().__init__("Group", resource_name=group.name)


# Exception for when a Group is not found
class GroupNotFound(resource.ResourceNotFound):
    def __init__(self, group_id: ResourceID):
        super().__init__("Group", resource_id=group_id)


# If user already exists in the group
class UserAlreadyExists(HTTPException):
    def __init__(self, user: Account, group: Group):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"User {user.email} already exists in group {group.name}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
        # logger.warning(self.detail)


# User not in the group
class UserNotInGroup(HTTPException):
    def __init__(self, user: Account, group: Group):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"User {user.email} not in group {group.name}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
        # return self.P
        # logger.warning(self.detail)


# Not authorized
class UserNotAuthorized(HTTPException):
    def __init__(self, user: Account, group: Group, action: str = "perform this action in"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN,
                         detail=f"User {user.email} is not authorized to {action} group {group.name}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail


# Exception for when a Group was not deleted successfully
class ErrorWhileDeleting(resource.ErrorWhileDeleting):
    def __init__(self, group_id: ResourceID):
        super().__init__("Workspace", resource_id=group_id)


# Exception for trying to add a member that already exists
class AddingExistingMember(HTTPException):
    def __init__(self, group: Group, member: Account):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"Member {member.email} already exists in {group.name} #{group.id}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
        # logger.warning(self.detail)


# Action not found
class ActionNotFound(resource.ActionNotFound):
    def __init__(self, action: str):
        super().__init__('group', action)


# User is not a member of the group
class UserNotMember(resource.UserNotMember):
    def __init__(self, group: Group, user: Account):
        super().__init__(group, user)
