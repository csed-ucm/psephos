# Account actions
from src import documents as Documents
from src.account_manager import current_active_user
from src.exceptions import account as AccountExceptions


# Delete account
async def delete_account(account: Documents.Account | None = None) -> None:
    if not account:
        account = current_active_user.get()

    # Delete account
    await Documents.Account.delete(account)

    # Delete all policies associated with account
    # BUG: This doesn't work due to type mismatch
    # await Documents.Policy.find({"policy_holder": account}).delete()  # type: ignore

    # Remove account from all workspaces
    workspaces = await Documents.Workspace.find(Documents.Workspace.members.id == account.id).to_list()  # type: ignore
    for workspace in workspaces:
        await workspace.remove_member(account)  # type: ignore

    # Remove account from all groups
    groups = await Documents.Group.find(Documents.Group.members.id == account.id).to_list()  # type: ignore
    for group in groups:
        await group.remove_member(account)  # type: ignore

    # Check if account was deleted
    if await Documents.Account.get(account.id):  # type: ignore
        raise AccountExceptions.ErrorWhileDeleting(account.id)  # type: ignore

    # Delete access tokens associated with account
    await Documents.AccessToken.find(Documents.AccessToken.user_id == account.id).delete()  # type: ignore
