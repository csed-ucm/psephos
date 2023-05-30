# Account actions
from app.models import documents as Documents
from app.account_manager import current_active_user
from app.exceptions import account as AccountExceptions


# Delete account
async def delete_account(account: Documents.Account | None = None) -> None:
    if not account:
        account = current_active_user.get()

    # Delete account
    # await account_manager.delete(account)
    await Documents.Account.delete(account)

    # Delete all policies associated with account
    # BUG: This doesn't work due to type mismatch
    # await Documents.Policy.find({"policy_holder": account}).delete()  # type: ignore

    # Remove account from all workspaces
    workspaces = await Documents.Workspace.find(Documents.Workspace.members.id == account.id).to_list()  # type: ignore
    for workspace in workspaces:
        await workspace.remove_member(account)  # type: ignore
        # await Documents.Workspace.save(workspace)

    # Remove account from all groups
    groups = await Documents.Group.find(Documents.Group.members.id == account.id).to_list()  # type: ignore
    for group in groups:
        await group.remove_member(account)  # type: ignore
        # await Documents.Group.save(group)

    # Check if account was deleted
    if await Documents.Account.get(account.id):  # type: ignore
        raise AccountExceptions.ErrorWhileDeleting(account.id)  # type: ignore
