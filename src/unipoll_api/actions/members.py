from beanie import WriteRules
from beanie.operators import In
from unipoll_api.documents import Account, Group, ResourceID, Workspace, Member
from unipoll_api.utils import Permissions
from unipoll_api.schemas import MemberSchemas
# from unipoll_api import AccountManager
from unipoll_api.exceptions import ResourceExceptions
from unipoll_api.dependencies import get_member


async def get_members(resource: Workspace | Group, check_permissions: bool = True) -> MemberSchemas.MemberList:
    # Check if the user has permission to add members
    await Permissions.check_permissions(resource, "get_members", check_permissions)

    def build_member_scheme(member: Member) -> MemberSchemas.Member:
        account: Account = member.account  # type: ignore
        return MemberSchemas.Member(id=member.id,
                                    account_id=account.id,
                                    first_name=account.first_name,
                                    last_name=account.last_name,
                                    email=account.email)

    member_list = [build_member_scheme(member) for member in resource.members]  # type: ignore
    # Return the list of members
    return MemberSchemas.MemberList(members=member_list)


# Add groups/members to group
async def add_members(resource: Workspace | Group,
                      account_id_list: list[ResourceID],
                      check_permissions: bool = True) -> MemberSchemas.MemberList:
    # Check if the user has permission to add members
    await Permissions.check_permissions(resource, "add_members", check_permissions)

    # Remove duplicates from the list of accounts
    accounts = set(account_id_list)
    # Remove existing members from the accounts set
    accounts = accounts.difference({member.id for member in resource.members})  # type: ignore
    # Find the accounts from the database
    account_list = await Account.find(In(Account.id, accounts)).to_list()
    # Add the accounts to the group member list with basic permissions

    new_members = []

    for account in account_list:
        default_permissions = eval("Permissions." + resource.get_document_type().upper() + "_BASIC_PERMISSIONS")
        if resource.get_document_type() == "Group":
            member = await get_member(account, resource.workspace)  # type: ignore
            new_member = await resource.add_member(member, default_permissions, save=False)
            new_members.append(new_member)
        elif resource.get_document_type() == "Workspace":
            new_member = await resource.add_member(account, default_permissions, save=False)
            new_members.append(new_member)
    await resource.save(link_rule=WriteRules.WRITE)  # type: ignore

    member_list = []
    for new_member in new_members:
        account: Account = new_member.account  # type: ignore
        member_list.append(MemberSchemas.Member(id=new_member.id,
                                                account_id=account.id,
                                                first_name=account.first_name,
                                                last_name=account.last_name,
                                                email=account.email))

    # Return the list of members added to the group
    return MemberSchemas.MemberList(members=member_list)


# Remove a member from a workspace
async def remove_member(resource: Workspace | Group,
                        member: Member,
                        permission_check: bool = True) -> MemberSchemas.MemberList:
    # Check if the user has permission to add members
    await Permissions.check_permissions(resource, "remove_members", permission_check)

    # Check if the account is a member of the workspace
    if member.id not in [ResourceID(member.id) for member in resource.members]:  # type: ignore
        raise ResourceExceptions.ResourceNotFound("Member", member.id)

    # Remove the account from the workspace/group
    if await resource.remove_member(member):
        # Return the list of members added to the group
        member_list = [MemberSchemas.Member(**account.model_dump()) for account in resource.members]  # type: ignore
        return MemberSchemas.MemberList(members=member_list)
    raise ResourceExceptions.ErrorWhileRemovingMember(resource, member)
