from fastapi import APIRouter, status, HTTPException, Depends
from src.account_manager import fastapi_users
from src.actions import account as AccountActions
from src.exceptions.resource import APIException
from src.models.documents import Account
from src.dependencies import get_account
from src.schemas import account as AccountSchemas


# APIRouter creates path operations for user module
router = APIRouter()


# Delete current user account
@router.delete("/me",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account():
    """
        ## Delete current user account

        This route deletes the account of the currently logged in user.

        ### Request body

        - **user** - User object

        ### Expected Response

        **204** - *The account has been deleted*
    """
    try:
        await AccountActions.delete_account()
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Delete user account by id
@router.delete("/{id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(account: Account = Depends(get_account)):
    """
        ## Delete current user account

        This route deletes the account of the currently logged in user.

        ### Request body

        - **user** - User object

        ### Expected Response

        **204** - *The account has been deleted*
    """
    try:
        await AccountActions.delete_account(account)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Update current user account
router.include_router(fastapi_users.get_users_router(AccountSchemas.Account, AccountSchemas.UpdateAccount))
