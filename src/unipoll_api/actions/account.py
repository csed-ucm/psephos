from unipoll_api.documents import Account, Workspace, Group, AccessToken
from unipoll_api.account_manager import active_user
from unipoll_api.exceptions import AccountExceptions


# Delete account
async def delete_account(account: Account | None = None) -> None:
    if not account:
        account = active_user.get()

    # Delete account
    await Account.delete(account)

    # Delete all policies associated with account
    # BUG: This doesn't work due to type mismatch
    # await Policy.find({"policy_holder": account}).delete()  # type: ignore

    # Remove account from all workspaces
    workspaces = await Workspace.find(Workspace.members.id == account.id).to_list()  # type: ignore
    for workspace in workspaces:
        await workspace.remove_member(account)  # type: ignore

    # Remove account from all groups
    groups = await Group.find(Group.members.id == account.id).to_list()  # type: ignore
    for group in groups:
        await group.remove_member(account)  # type: ignore

    # Check if account was deleted
    if await Account.get(account.id):  # type: ignore
        raise AccountExceptions.ErrorWhileDeleting(account.id)  # type: ignore

    # Delete access tokens associated with account
    await AccessToken.find(AccessToken.user_id == account.id).delete()  # type: ignore
