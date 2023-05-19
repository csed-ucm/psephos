from fastapi import APIRouter, status, HTTPException
from app.actions import account as AccountActions
from app.models.documents import ResourceID
from app.exceptions.resource import APIException


# APIRouter creates path operations for user module
router = APIRouter()


# Delete current user account
@router.delete("/me")
async def delete_user(account_id: ResourceID | None = None):
    """
        ## Delete current user account

        This route deletes the account of the currently logged in user.

        ### Request body

        - **user** - User object

        ### Expected Response

        **204** - *The account has been deleted*
    """
    try:
        await AccountActions.delete_account(account_id)
        return status.HTTP_204_NO_CONTENT
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))
