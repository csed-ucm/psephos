from fastapi import HTTPException, status
from app.utils.colored_dbg import print_warning


class ExistsWithSuchName(HTTPException):
    def __init__(self, workspace_name: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"Workspace with name \"{workspace_name}\" already exists")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
        # logger.warning(self.detail)


class ErrorWhileCreating(HTTPException):
    def __init__(self, workspace_name: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail=f"Error while creating workspace {workspace_name}")

    def __str__(self) -> str:
        print_warning(self.detail)
        return self.detail
        # logger.warning(self.detail)