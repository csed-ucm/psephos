from typing import Union
from fastapi import HTTPException
from app.models.documents import ResourceID
from app.utils.colored_dbg import print_warning


class AccountNotFound(HTTPException):
    def __init__(self, account: Union[ResourceID, str, None] = None):
        message = "Account not found"  # Default message
        if account:
            if account.__class__ == ResourceID:
                message = f"Account with id {account} not found"
            elif account.__class__ == str:
                message = f"Account with email {account} not found"
            # elif account.__class__ == str:
            #     message = f"Account with name {account} not found"
        super().__init__(status_code=404, detail=message)

    def __str__(self) -> str:
        # logger.warning(self.detail)
        print_warning(self.detail)
        return self.detail
