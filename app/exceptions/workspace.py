from fastapi import HTTPException, status
from app.models.documents import ResourceID, Workspace, Account
from app.exceptions import resource
from app.utils.colored_dbg import print_warning


# Exception for when a Workspace with the same name already exists
class NonUniqueName(resource.NonUniqueName):
    def __init__(self, workspace_name: str):
        super().__init__("Workspace", resource_name=workspace_name)


# Exception for when an error occurs during Workspace creation
class ErrorWhileCreating(resource.ErrorWhileCreating):
    def __init__(self, workspace_name: str):
        super().__init__("Workspace", resource_name=workspace_name)


# Exception for when a Workspace is not found
class WorkspaceNotFound(resource.ResourceNotFound):
    def __init__(self, workspace_id: ResourceID):
        super().__init__("Workspace", resource_id=workspace_id)


# Exception for trying to add a member that already exists
class AddingExistingMember(HTTPException):
    def __init__(self, workspace: Workspace, member: Account):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"Member {member.email} already exists in {workspace.name} #{workspace.id}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
        # logger.warning(self.detail)


# Exception for when a Workspace was not deleted successfully
class ErrorWhileDeleting(resource.ErrorWhileDeleting):
    def __init__(self, workspace_id: ResourceID):
        super().__init__("Workspace", resource_id=workspace_id)


class UserNotMember(resource.UserNotMember):
    def __init__(self, workspace: Workspace, user: Account):
        super().__init__(workspace, user)


# Not authorized
class UserNotAuthorized(resource.UserNotAuthorized):
    def __init__(self, account: Account, workspace: Workspace, action: str = "perform this action in"):
        super().__init__(account, f"workspace {workspace.name}", action)


# Action not found
class ActionNotFound(resource.ActionNotFound):
    def __init__(self, action: str):
        super().__init__('workspace', action)
