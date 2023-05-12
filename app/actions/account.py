from beanie.operators import In
from app.models.group import Group
from app.models.account import Account
from app.models.resource import ResourceID
from pydantic import EmailStr
from app.schemas.group import GroupReadShort, GroupList
from app.exceptions.account import AccountNotFound


# Get all groups that a account is a member of with the account's role in that group
async def get_account_groups(account: Account) -> GroupList:
    """Get all groups that a account is a member of.
    The function returns a list of dictionaries with role as a key and and a list of groups as a value.

    Args:
        account (Account): Account object with list of group ids

    Returns:
        GroupList: Model with the list of groups that account belongs to and the account's role in that group.
    """
    # groups = await Group.find(In(Group.id, account.groups)).to_list()
    result = []
    # for group in groups:
    #     if account.id == group.owner:
    #         result.append(GroupReadShort(name=group.name, role="owner"))
    #     elif account.id in group.admins:
    #         result.append(GroupReadShort(name=group.name, role="admin"))
    #     elif account.id in group.members:
    #         result.append(GroupReadShort(name=group.name, role="account"))

    group_list = GroupList(groups=result)
    return group_list


# Check if account exists in the database
async def check_account_exists(account: Account | ResourceID | EmailStr) -> Account:
    """Check if account exists in the database

    Args:
        account (Account): Account object

    Returns:
        Account: returns Account object of found account, raises a HTTP exception otherwise
    """
    if isinstance(account, Account):
        found_account = await Account.get(account.id)
    elif isinstance(account, ResourceID):
        found_account = await Account.get(account)
    elif isinstance(account, EmailStr):
        found_account = await Account.find_one({"email": account})
    else:
        # Display error message with the type of the account object
        raise TypeError("Invalid type for account", type(account))

    if not found_account:
        raise AccountNotFound(str(account))
    return found_account
