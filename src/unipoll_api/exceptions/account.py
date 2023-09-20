from src.exceptions import resource
from src.documents import ResourceID


class AccountNotFound(resource.ResourceNotFound):
    def __init__(self, account_id: ResourceID):
        super().__init__("Account", resource_id=account_id)


class ErrorWhileDeleting(resource.ErrorWhileDeleting):
    def __init__(self, account_id: ResourceID):
        super().__init__("Account", resource_id=account_id)
