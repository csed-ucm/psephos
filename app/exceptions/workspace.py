from app.exceptions import resource
from app.schemas.workspace import WorkspaceID


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
    def __init__(self, workspace_id: WorkspaceID):
        super().__init__("Workspace", resource_id=workspace_id)
