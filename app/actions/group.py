from beanie.operators import In
from app.account_manager import current_active_user
from app.models.documents import Policy, ResourceID, Workspace, Group, Account
from app.schemas import account as AccountSchemas
from app.schemas import group as GroupSchemas
from app.schemas import policy as PolicySchemas
from app.schemas import workspace as WorkspaceSchema
from app.schemas import member as MemberSchemas
from app.exceptions import account as AccountExceptions
from app.exceptions import group as GroupExceptions
from app.exceptions import workspace as WorkspaceExceptions
from app.exceptions import resource as GenericExceptions
from app.utils import colored_dbg
from app.utils import permissions as Permissions


# Get all groups (for superuser)
# async def get_all_groups() -> GroupSchemas.GroupList:
#     group_list = []
#     search_result = await Group.find_all().to_list()

#     # Create a group list for output schema using the search results
#     for group in search_result:
#         group_list.append(GroupSchemas.Group(**group.dict()))

#     return GroupSchemas.GroupList(groups=group_list)


# Get group by id
async def get_group(group: Group) -> GroupSchemas.Group:
    # Create a group list for output schema using the search results
    await group.fetch_all_links()
    member_list = []
    policy_list = []
    group_list = []
    for member in group.members:
        member_list.append(AccountSchemas.AccountShort(**member.dict()))  # type: ignore
    for policy in group.policies:
        policy_list.append(PolicySchemas.PolicyShort(**policy.dict(exclude={"policy_holder"}),  # type: ignore
                                                     policy_holder=policy.policy_holder))  # type: ignore

    res = GroupSchemas.Group(id=group.id, name=group.name, description=group.description,
                             workspace=WorkspaceSchema.WorkspaceShort(**group.workspace.dict()),  # type: ignore
                             members=member_list,
                             policies=policy_list,
                             groups=group_list)
    return res


# Update a group
async def update_group(group: Group, group_data: GroupSchemas.GroupUpdateIn) -> GroupSchemas.Group:
    # workspace = await Workspace.get(group.workspace)
    await group.fetch_link(Group.workspace)
    workspace: Workspace = group.workspace  # type: ignore

    # The group must belong to a workspace
    if not workspace:
        raise WorkspaceExceptions.WorkspaceNotFound(workspace)

    # Check if no updates are provided
    if not group_data.name and not group_data.description:
        return GroupSchemas.Group(**group.dict())

    # Update the group
    if group_data.name:
        # Check if group name is unique
        await workspace.fetch_link(Workspace.groups)
        for _group in workspace.groups:
            if _group.name == group_data.name:  # type: ignore
                raise GroupExceptions.NonUniqueName(group)
        group.name = group_data.name  # Update the group name
    if group_data.description:
        group.description = group_data.description  # Update the group description

    # Save the updates
    await Group.save(group)
    return GroupSchemas.Group(**group.dict())


# Delete a group
async def delete_group(group: Group):
    # await Group.delete(group) # link_rule=DeleteRules.DELETE_LINKS
    await Group.delete(group)

    # workspace = await Workspace.get(group.workspace)
    await group.fetch_link(Group.workspace)
    workspace: Workspace = group.workspace  # type: ignore

    if workspace:
        workspace.groups = [g for g in workspace.groups if g.id != group.id]
        await Workspace.save(workspace)

    if await Group.get(group.id):
        return GroupExceptions.ErrorWhileDeleting(group.id)


# Get list of members of a group
async def get_group_members(group: Group) -> MemberSchemas.MemberList:
    await group.fetch_link(Group.members)

    member_list = []
    member: Account
    for member in group.members:  # type: ignore
        member_data = member.dict(include={'id', 'first_name', 'last_name', 'email'})
        member_scheme = MemberSchemas.Member(**member_data)
        member_list.append(member_scheme)
    return MemberSchemas.MemberList(members=member_list)


# Add groups/members to group
async def add_group_members(group: Group, member_data: MemberSchemas.AddMembers):
    accounts = set(member_data.accounts)

    # Remove existing members from the accounts set
    accounts = accounts.difference({member.ref.id for member in group.members})

    # Find the accounts from the database
    account_list = await Account.find(In(Account.id, accounts)).to_list()

    # Default policy(permissions) for the new members
    default_permissions: Permissions.GroupPermissions = Permissions.GroupPermissions(1)  # type: ignore

    # Add the accounts to the group member list with default permissions
    for account in account_list:
        await group.add_member(group.workspace, account, default_permissions)
        colored_dbg.info(f'Account {account.id} has been added to workspace {group.id} as a member.')
    await Group.save(group)

    # Return the list of members added to the group
    return MemberSchemas.MemberList(members=[MemberSchemas.Member(**account.dict()) for account in account_list])


# Remove a member from a workspace
async def remove_group_member(group: Group, account_id: ResourceID | None):
    # Check if account_id is specified in request, if account_id is not specified, use the current user
    if account_id:
        account = await Account.get(account_id)  # type: ignore
        if not account:
            raise AccountExceptions.AccountNotFound(account_id)
    else:
        account = current_active_user.get()

    if account.id not in [ResourceID(member.ref.id) for member in group.members]:
        raise GroupExceptions.UserNotMember(group, account)
    return await group.remove_member(account)


# List all permissions for a user in a workspace
async def get_group_permissions(group: Group, account_id: ResourceID | None):
    # Check if account_id is specified in request, if account_id is not specified, use the current user
    if account_id:
        account = await Account.get(account_id)  # type: ignore
        if not account:
            raise AccountExceptions.AccountNotFound(account_id)
    else:
        account = current_active_user.get()

    # Check if account is a member of the group
    if account.id not in [member.ref.id for member in group.members]:
        raise GroupExceptions.UserNotMember(group, account)

    await group.fetch_link(Group.policies)
    user_permissions = await Permissions.get_all_permissions(group, account)
    res = {'permissions': Permissions.GroupPermissions(user_permissions).name.split('|'),  # type: ignore
           'account': AccountSchemas.AccountShort(**account.dict())}
    return res


async def set_group_permissions(group: Group, input_data: PolicySchemas.PolicyInput):
    account: Account = current_active_user.get()
    await group.fetch_link(group.policies)
    # Find the policy for the account
    policy: Policy
    for policy in group.policies:  # type: ignore
        if policy.policy_holder == account:
            new_permission_value = 0
            for i in input_data.permissions:
                try:
                    new_permission_value += Permissions.GroupPermissions[i].value  # type: ignore
                except KeyError:
                    raise GenericExceptions.InvalidPermission(i)
            policy.permissions = Permissions.GroupPermissions(new_permission_value)  # type: ignore
            # print(policy.permissions)
            await Policy.save(policy)
            return {'permissions': Permissions.GroupPermissions(policy.permissions).name.split('|')}  # type: ignore
    raise GroupExceptions.UserNotMember(group, account)
