from beanie import DeleteRules
from beanie.operators import In
from src.account_manager import current_active_user
from src.models.documents import Policy, ResourceID, Workspace, Group, Account
from src.schemas import account as AccountSchemas
from src.schemas import group as GroupSchemas
from src.schemas import policy as PolicySchemas
from src.schemas import workspace as WorkspaceSchema
from src.schemas import member as MemberSchemas
from src.exceptions import account as AccountExceptions
from src.exceptions import group as GroupExceptions
from src.exceptions import workspace as WorkspaceExceptions
from src.exceptions import resource as GenericExceptions
from src.exceptions import policy as PolicyExceptions
from src.utils import permissions as Permissions


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
    member_list: list[Account] = []
    policy_list: list[Policy] = []
    group_list: list[Group] = []
    for member in group.members:
        member_list.append(AccountSchemas.AccountShort(**member.dict()))  # type: ignore
    for policy in group.policies:
        policy_list.append(PolicySchemas.PolicyShort(**policy.dict(exclude={"policy_holder"}),  # type: ignore
                                                     policy_holder=policy.policy_holder))  # type: ignore

    return GroupSchemas.Group(id=group.id, name=group.name, description=group.description,
                              workspace=WorkspaceSchema.WorkspaceShort(
                                  **group.workspace.dict()),  # type: ignore
                              members=member_list,
                              policies=policy_list,
                              groups=group_list)


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
        # NOTE: This is causing error because the links are fetched already
        # await workspace.fetch_link("groups")
        for g in workspace.groups:
            if g.name == group_data.name:  # type: ignore
                raise GroupExceptions.NonUniqueName(group)
        group.name = group_data.name  # Update the group name
    if group_data.description:
        group.description = group_data.description  # Update the group description

    # Save the updates
    await Group.save(group)
    return GroupSchemas.Group(**group.dict())


# Delete a group
async def delete_group(group: Group):
    await group.fetch_link(Group.workspace)
    workspace: Workspace = group.workspace  # type: ignore
    workspace.groups = [g for g in workspace.groups if g.id != group.id]  # type: ignore
    workspace.policies = [p for p in workspace.policies if p.policy_holder.ref.id != group.id]  # type: ignore
    await Workspace.save(workspace, link_rule=DeleteRules.DELETE_LINKS)
    await Group.delete(group)

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
async def add_group_members(group: Group, member_data: MemberSchemas.AddMembers) -> MemberSchemas.MemberList:
    accounts = set(member_data.accounts)

    # Remove existing members from the accounts set
    accounts = accounts.difference({member.ref.id for member in group.members})

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
        account = current_active_user.get()

    # Check if the account exists
    if not account:
        raise GenericExceptions.InternalServerError("remove_group_member() -> Account not found")

    if account.id not in [ResourceID(member.ref.id) for member in group.members]:
        raise GroupExceptions.UserNotMember(group, account)
    return await group.remove_member(account)


# Get all policies of a group
async def get_group_policies(group: Group) -> PolicySchemas.PolicyList:
    policy_list = []
    await group.fetch_link("policies")
    policy: Policy
    for policy in group.policies:  # type: ignore
        permissions = Permissions.GroupPermissions(policy.permissions).name.split('|')  # type: ignore
        # BUG: Beanie cannot fetch policy_holder link, as it can be a Group or an Account
        # BUG: Group type is selected by default, so it cannot find Account in the Group collection
        # await policy.fetch_link(Policy.policy_holder)

        # FIXME: This is a workaround for the above bug
        if policy.policy_holder_type == 'account':
            policy_holder = await Account.get(policy.policy_holder.ref.id)
        elif policy.policy_holder_type == 'group':
            policy_holder = await Group.get(policy.policy_holder.ref.id)
        else:
            raise GenericExceptions.InternalServerError("Invalid policy_holder_type")

        if not policy_holder:
            raise GenericExceptions.InternalServerError("get_group_policies() => Policy holder not found")

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
        account = current_active_user.get()

    if not account:
        raise GenericExceptions.InternalServerError("get_group_policy() => Account not found")

    # Check if account is a member of the group
    if account.id not in [member.ref.id for member in group.members]:
        raise GroupExceptions.UserNotMember(group, account)

    await group.fetch_link(Group.policies)
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
            account = current_active_user.get()

        if not account:
            raise GenericExceptions.InternalServerError("set_group_policy() => Account not found")

        await group.fetch_link("policies")
        # Find the policy for the account
        # NOTE: To set a policy for a user, the user must be a member of the workspace, therefore the policy must exist
        p: Policy
        for p in group.policies:  # type: ignore
            if p.policy_holder_type == "account":
                if p.policy_holder.ref.id == account.id:
                    policy = p
                    break
    new_permission_value = 0
    for i in input_data.permissions:
        try:
            new_permission_value += Permissions.GroupPermissions[i].value  # type: ignore
        except KeyError:
            raise GenericExceptions.InvalidPermission(i)
    policy.permissions = Permissions.GroupPermissions(new_permission_value)  # type: ignore
    await Policy.save(policy)

    return PolicySchemas.PolicyOutput(
        permissions=Permissions.GroupPermissions(policy.permissions).name.split('|'),  # type: ignore
        policy_holder=MemberSchemas.Member(**account.dict()))  # type: ignore
