from beanie import WriteRules
from beanie.operators import In
from unipoll_api.documents import Account, Group, ResourceID, Workspace
from unipoll_api.utils import Permissions
from unipoll_api.schemas import MemberSchemas
from unipoll_api import AccountManager
from unipoll_api.exceptions import ResourceExceptions


async def get_members(resource: Workspace | Group) -> MemberSchemas.MemberList:
    account = AccountManager.active_user.get()
    permissions = await Permissions.get_all_permissions(resource, account)

    if resource.resource_type == "workspace":
        req_permissions = Permissions.WorkspacePermissions["get_workspace_members"]  # type: ignore
    elif resource.resource_type == "group":
        req_permissions = Permissions.GroupPermissions["get_group_members"]  # type: ignore
    else:
        raise ResourceExceptions.InternalServerError("Invalid resource type")

    if not Permissions.check_permission(permissions, req_permissions):
        ResourceExceptions.UserNotAuthorized(account, resource.resource_type, "to view members")

    def build_member_scheme(member: Account) -> MemberSchemas.Member:
        member_data = member.model_dump(include={'id', 'first_name', 'last_name', 'email'})
        member_scheme = MemberSchemas.Member(**member_data)
        return member_scheme

    member_list = [build_member_scheme(member) for member in resource.members]  # type: ignore
    # Return the list of members
    return MemberSchemas.MemberList(members=member_list)


# Add groups/members to group
async def add_members(resource: Workspace | Group,
                      account_id_list: list[ResourceID]) -> MemberSchemas.MemberList:
    # Check if the user has permission to add members
    account = AccountManager.active_user.get()
    permissions = await Permissions.get_all_permissions(resource, account)
    if resource.resource_type == "workspace":
        req_permissions = Permissions.WorkspacePermissions["add_workspace_members"]
        default_permissions = Permissions.WORKSPACE_BASIC_PERMISSIONS
    elif resource.resource_type == "group":
        req_permissions = Permissions.GroupPermissions["add_group_members"]  # type: ignore
        default_permissions = Permissions.GROUP_BASIC_PERMISSIONS  # type: ignore
    else:
        raise ResourceExceptions.InternalServerError("Invalid resource type")

    if not Permissions.check_permission(permissions, req_permissions):
        ResourceExceptions.UserNotAuthorized(account, resource.resource_type, "to add members")

    # Remove duplicates from the list of accounts
    accounts = set(account_id_list)
    # Remove existing members from the accounts set
    accounts = accounts.difference({member.id for member in resource.members})  # type: ignore
    # Find the accounts from the database
    account_list = await Account.find(In(Account.id, accounts)).to_list()
    # Add the accounts to the group member list with basic permissions

    for account in account_list:
        await resource.add_member(account, default_permissions, save=False)
    await resource.save(link_rule=WriteRules.WRITE)  # type: ignore

    # Return the list of members added to the group
    return MemberSchemas.MemberList(members=[MemberSchemas.Member(**account.model_dump()) for account in account_list])


# Remove a member from a workspace
async def remove_member(resource: Workspace | Group, account: Account):
    # Check if the user has permission to add members
    account = AccountManager.active_user.get()
    permissions = await Permissions.get_all_permissions(resource, account)
    if resource.resource_type == "workspace":
        req_permissions = Permissions.WorkspacePermissions["remove_workspace_members"]  # type: ignore
    elif resource.resource_type == "group":
        req_permissions = Permissions.GroupPermissions["remove_group_members"]  # type: ignore
    else:
        raise ResourceExceptions.InternalServerError("Invalid resource type")
    if not Permissions.check_permission(permissions, req_permissions):
        ResourceExceptions.UserNotAuthorized(account, resource.resource_type, "to add members")

    # Check if the account is a member of the workspace
    if account.id not in [ResourceID(member.id) for member in resource.members]:  # type: ignore
        raise ResourceExceptions.UserNotMember(resource, account)

    # Remove the account from the workspace/group
    if await resource.remove_member(account):
        # Return the list of members added to the group
        member_list = [MemberSchemas.Member(**account.model_dump()) for account in resource.members]  # type: ignore
        return MemberSchemas.MemberList(members=member_list)
    raise ResourceExceptions.ErrorWhileRemovingMember(resource, account)
