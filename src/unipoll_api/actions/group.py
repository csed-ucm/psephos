from beanie import DeleteRules
from beanie.operators import In
from unipoll_api import AccountManager
from unipoll_api.documents import Policy, ResourceID, Workspace, Group, Account
from unipoll_api.schemas import AccountSchemas, GroupSchemas, MemberSchemas, PolicySchemas, WorkspaceSchemas
from unipoll_api.exceptions import (AccountExceptions, GroupExceptions, PolicyExceptions,
                                    ResourceExceptions, WorkspaceExceptions)
from unipoll_api.utils import permissions as Permissions


# Get all groups (for superuser)
# async def get_all_groups() -> GroupSchemas.GroupList:
#     group_list = []
#     search_result = await Group.find_all().to_list()

#     # Create a group list for output schema using the search results
#     for group in search_result:
#         group_list.append(GroupSchemas.Group(**group.dict()))

#     return GroupSchemas.GroupList(groups=group_list)


# Get group
async def get_group(group: Group, include_members: bool = False, include_policies: bool = False) -> GroupSchemas.Group:
    members = None
    policies = None

    account = AccountManager.active_user.get()
    # Get the permissions(allowed actions) of the current user
    permissions = await Permissions.get_all_permissions(group, account)
    # Fetch the resources if the user has the required permissions
    if include_members:
        req_permissions = Permissions.GroupPermissions["get_group_members"]  # type: ignore
        if Permissions.check_permission(permissions, req_permissions):
            members = (await get_group_members(group)).members
    if include_policies:
        req_permissions = Permissions.GroupPermissions["get_group_policies"]  # type: ignore
        if Permissions.check_permission(permissions, req_permissions):
            policies = (await get_group_policies(group)).policies

    workspace = WorkspaceSchemas.Workspace(**group.workspace.dict(exclude={"members",  # type: ignore
                                                                           "policies",
                                                                           "groups"}))

    # Return the workspace with the fetched resources
    return GroupSchemas.Group(id=group.id,
                              name=group.name,
                              description=group.description,
                              workspace=workspace,
                              members=members,
                              policies=policies)


# Update a group
async def update_group(group: Group,
                       group_data: GroupSchemas.GroupUpdateRequest) -> GroupSchemas.Group:
    save_changes = False
    workspace: Workspace = group.workspace  # type: ignore
    # The group must belong to a workspace
    if not workspace:
        raise WorkspaceExceptions.WorkspaceNotFound(workspace)

    # Check if group name is provided
    if group_data.name and group_data.name != group.name:
        # Check if group name is unique
        for g in workspace.groups:
            if g.name == group_data.name:  # type: ignore
                raise GroupExceptions.NonUniqueName(group)
        group.name = group_data.name  # Update the group name
        save_changes = True
    # Check if group description is provided
    if group_data.description and group_data.description != group.description:
        group.description = group_data.description  # Update the group description
        save_changes = True

    # Save the updates
    if save_changes:
        await Group.save(group)
    # Return the updated group
    return GroupSchemas.Group(**group.dict())


# Delete a group
async def delete_group(group: Group):
    # await group.fetch_link(Group.workspace)
    workspace: Workspace = group.workspace  # type: ignore
    workspace.groups = [g for g in workspace.groups if g.id != group.id]  # type: ignore
    workspace.policies = [p for p in workspace.policies if p.policy_holder.ref.id != group.id]  # type: ignore
    await Workspace.save(workspace, link_rule=DeleteRules.DELETE_LINKS)
    await Group.delete(group)

    if await Group.get(group.id):
        return GroupExceptions.ErrorWhileDeleting(group.id)


# Get list of members of a group
async def get_group_members(group: Group) -> MemberSchemas.MemberList:
    member_list = []
    member: Account
    for member in group.members:  # type: ignore
        member_data = member.dict(include={'id', 'first_name', 'last_name', 'email'})
        member_scheme = MemberSchemas.Member(**member_data)
        member_list.append(member_scheme)
    # Return the list of members
    return MemberSchemas.MemberList(members=member_list)


# Add groups/members to group
async def add_group_members(group: Group, member_data: MemberSchemas.AddMembers) -> MemberSchemas.MemberList:
    accounts = set(member_data.accounts)
    # Remove existing members from the accounts set
    accounts = accounts.difference({member.id for member in group.members})  # type: ignore
    # Find the accounts from the database
    account_list = await Account.find(In(Account.id, accounts)).to_list()
    # Add the accounts to the group member list with default permissions
    for account in account_list:
        await group.add_member(group.workspace, account, Permissions.GROUP_BASIC_PERMISSIONS)
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
        account = AccountManager.active_user.get()
    # Check if the account exists
    if not account:
        raise ResourceExceptions.InternalServerError("remove_group_member() -> Account not found")
    # Check if account is a member of the group
    if account.id not in [ResourceID(member.ref.id) for member in group.members]:
        raise GroupExceptions.UserNotMember(group, account)
    # Remove the account from the group
    if await group.remove_member(account):
        member_list = [MemberSchemas.Member(**account.dict()) for account in group.members]  # type: ignore
        return MemberSchemas.MemberList(members=member_list)
    raise GroupExceptions.ErrorWhileRemovingMember(group, account)


# Get all policies of a group
async def get_group_policies(group: Group) -> PolicySchemas.PolicyList:
    policy_list = []
    policy: Policy
    for policy in group.policies:  # type: ignore
        permissions = Permissions.GroupPermissions(policy.permissions).name.split('|')  # type: ignore
        # Get the policy_holder
        if policy.policy_holder_type == 'account':
            policy_holder = await Account.get(policy.policy_holder.ref.id)
        elif policy.policy_holder_type == 'group':
            policy_holder = await Group.get(policy.policy_holder.ref.id)
        else:
            raise ResourceExceptions.InternalServerError("Invalid policy_holder_type")
        if not policy_holder:
            # TODO: Replace with custom exception
            raise ResourceExceptions.InternalServerError("get_group_policies() => Policy holder not found")
        # Convert the policy_holder to a Member schema
        policy_holder = MemberSchemas.Member(**policy_holder.dict())  # type: ignore
        policy_list.append(PolicySchemas.PolicyShort(id=policy.id,
                                                     policy_holder_type=policy.policy_holder_type,
                                                     # Exclude unset fields(i.e. "description" for Account)
                                                     policy_holder=policy_holder.dict(exclude_unset=True),
                                                     permissions=permissions))
    return PolicySchemas.PolicyList(policies=policy_list)


# List all permissions for a user in a workspace
async def get_group_policy(group: Group, account_id: ResourceID | None):
    # Check if account_id is specified in request, if account_id is not specified, use the current user
    if account_id:
        account = await Account.get(account_id)  # type: ignore
        if not account:
            raise AccountExceptions.AccountNotFound(account_id)
    else:
        account = AccountManager.active_user.get()

    if not account:
        raise ResourceExceptions.InternalServerError("get_group_policy() => Account not found")

    # Check if account is a member of the group
    # if account.id not in [member.id for member in group.members]:
    if account not in group.members:
        raise GroupExceptions.UserNotMember(group, account)

    # await group.fetch_link(Group.policies)
    user_permissions = await Permissions.get_all_permissions(group, account)
    res = {'permissions': Permissions.GroupPermissions(user_permissions).name.split('|'),  # type: ignore
           'account': AccountSchemas.AccountShort(**account.dict())}
    return res


async def set_group_policy(group: Group,
                           input_data: PolicySchemas.PolicyInput) -> PolicySchemas.PolicyOutput:
    policy: Policy | None = None
    account: Account | None = None
    if input_data.policy_id:
        policy = await Policy.get(input_data.policy_id)
        if not policy:
            raise PolicyExceptions.PolicyNotFound(input_data.policy_id)
        # BUG: Beanie cannot fetch policy_holder link, as it can be a Group or an Account
        else:
            account = await Account.get(policy.policy_holder.ref.id)
    else:
        if input_data.account_id:
            account = await Account.get(input_data.account_id)
            if not account:
                raise AccountExceptions.AccountNotFound(input_data.account_id)
        else:
            account = AccountManager.active_user.get()
        # Make sure the account is loaded
        if not account:
            raise ResourceExceptions.InternalServerError("set_group_policy() => Account not found")
        try:
            # Find the policy for the account
            # NOTE: To set a policy for a user, the user must be a member of the group, therefore the policy must exist
            p: Policy
            for p in group.policies:  # type: ignore
                if p.policy_holder_type == "account":
                    if p.policy_holder.ref.id == account.id:
                        policy = p
                        break
        except Exception as e:
            raise ResourceExceptions.InternalServerError(str(e))
    # Calculate the new permission value
    new_permission_value = 0
    for i in input_data.permissions:
        try:
            new_permission_value += Permissions.GroupPermissions[i].value  # type: ignore
        except KeyError:
            raise ResourceExceptions.InvalidPermission(i)
    # Update the policy
    policy.permissions = Permissions.GroupPermissions(new_permission_value)  # type: ignore
    await Policy.save(policy)

    # Get Account or Group from policy_holder link
    # HACK: Have to do it manualy, as Beanie cannot fetch policy_holder link of mixed types (Account | Group)
    if policy.policy_holder_type == "account":  # type: ignore
        policy_holder = await Account.get(policy.policy_holder.ref.id)  # type: ignore
    elif policy.policy_holder_type == "group":  # type: ignore
        policy_holder = await Group.get(policy.policy_holder.ref.id)  # type: ignore

    # Return the updated policy
    return PolicySchemas.PolicyOutput(
        permissions=Permissions.GroupPermissions(policy.permissions).name.split('|'),  # type: ignore
        policy_holder=MemberSchemas.Member(**policy_holder.dict()))  # type: ignore
