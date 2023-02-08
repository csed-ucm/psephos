from fastapi import HTTPException, status
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
