from fastapi import APIRouter, status, HTTPException, Depends
from unipoll_api.account_manager import fastapi_users
from unipoll_api.actions import AccountActions
from unipoll_api.exceptions.resource import APIException
from unipoll_api.documents import Account
from unipoll_api.dependencies import get_account
from unipoll_api.schemas import AccountSchemas


# APIRouter creates path operations for user module
router: APIRouter = APIRouter()


@router.get("",
            response_model=AccountSchemas.AccountList)
async def get_all_accounts():
    try:
        accounts = [AccountSchemas.AccountShort(**a.model_dump()) for a in await Account.find_all().to_list()]
        return AccountSchemas.AccountList(accounts=accounts)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


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
