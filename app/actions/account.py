# Account actions
from app.models.documents import Account, ResourceID
from app.account_manager import current_active_user
from app.exceptions import account as AccountExceptions


# Delete account
async def delete_account(account_id: ResourceID | None) -> None:
    account: Account = await Account.get(account_id) if account_id else current_active_user.get()  # type: ignore

    # Check if account exists
    if not account and account_id:
        raise AccountExceptions.AccountNotFound(account_id)

    # Delete account
    await Account.delete(account)

    # Check if account was deleted
    if await Account.get(account.id):
        raise AccountExceptions.ErrorWhileDeleting(account.id)
