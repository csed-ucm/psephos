# from typing import Optional
# from pydantic import EmailStr
from beanie import WriteRules, DeleteRules
from beanie.operators import In
from src.account_manager import current_active_user
from src.documents import Group, ResourceID, Workspace, Account, Policy, create_link
from src.schemas import workspace as WorkspaceSchemas
# from app.schemas import account as AccountSchemas
from src.schemas import group as GroupSchemas
from src.schemas import policy as PolicySchemas
from src.schemas import member as MemberSchemas
from src.exceptions import workspace as WorkspaceExceptions
from src.exceptions import account as AccountExceptions
from src.exceptions import group as GroupExceptions
from src.exceptions import resource as GenericExceptions
from src.exceptions import policy as PolicyExceptions
from src.utils import permissions as Permissions


# Get a list of workspaces where the account is a owner/member
async def get_workspaces() -> WorkspaceSchemas.WorkspaceList:
    account = current_active_user.get()
    workspace_list = []

    search_result = await Workspace.find(Workspace.members.id == account.id).to_list()  # type: ignore

    # Create a workspace list for output schema using the search results
    for workspace in search_result:
        workspace_list.append(WorkspaceSchemas.WorkspaceShort(
            **workspace.dict(exclude={'members', 'groups', 'permissions'})))

    return WorkspaceSchemas.WorkspaceList(workspaces=workspace_list)


# Create a new workspace with account as the owner
async def create_workspace(input_data: WorkspaceSchemas.WorkspaceCreateInput) -> WorkspaceSchemas.WorkspaceCreateOutput:
    account: Account = current_active_user.get()
    # Check if workspace name is unique
    if await Workspace.find_one({"name": input_data.name}):
        raise WorkspaceExceptions.NonUniqueName(input_data.name)

    # Create a new workspace
    new_workspace = await Workspace(name=input_data.name, description=input_data.description).create()

    # Check if workspace was created
    if not new_workspace:
        raise WorkspaceExceptions.ErrorWhileCreating(input_data.name)

    # Create a policy for the new member
    # The member(creator) has full permissions on the workspace
    new_policy = Policy(policy_holder_type='account',
                        policy_holder=(await create_link(account)),
                        permissions=Permissions.WORKSPACE_ALL_PERMISSIONS,
                        workspace=new_workspace)  # type: ignore

    # Add the current user and the policy to workspace member list
    new_workspace.members.append(account)  # type: ignore
    new_workspace.policies.append(new_policy)  # type: ignore
    await Workspace.save(new_workspace, link_rule=WriteRules.WRITE)

    # Specify fields for output schema
    return WorkspaceSchemas.WorkspaceCreateOutput(**new_workspace.dict())


# Get a workspace
async def get_workspace(workspace: Workspace) -> Workspace:
    return workspace


# Update a workspace
async def update_workspace(workspace: Workspace,
                           input_data: WorkspaceSchemas.WorkspaceUpdateRequest) -> WorkspaceSchemas.Workspace:
    save_changes = False
    # Check if user suplied a name
    if input_data.name and input_data.name != workspace.name:
        # Check if workspace name is unique
        if await Workspace.find_one({"name": input_data.name}) and workspace.name != input_data.name:
            raise WorkspaceExceptions.NonUniqueName(input_data.name)
        workspace.name = input_data.name  # Update the name
        save_changes = True
    # Check if user suplied a description
    if input_data.description and input_data.description != workspace.description:
        workspace.description = input_data.description  # Update the description
        save_changes = True
    # Save the updated workspace
    if save_changes:
        await Workspace.save(workspace)
    # Return the updated workspace
    return WorkspaceSchemas.Workspace(**workspace.dict())


# Delete a workspace
async def delete_workspace(workspace: Workspace):
    await Workspace.delete(workspace, link_rule=DeleteRules.DO_NOTHING)
    # await Workspace.delete(workspace, link_rule=DeleteRules.DELETE_LINKS)
    if await workspace.get(workspace.id):
        raise WorkspaceExceptions.ErrorWhileDeleting(workspace.id)
    await Policy.find(Policy.workspace.id == workspace.id).delete()  # type: ignore
    await Group.find(Group.workspace.id == workspace).delete()  # type: ignore


# List all members of a workspace
async def get_workspace_members(workspace: Workspace) -> MemberSchemas.MemberList:
    member_list = []
    member: Account
    for member in workspace.members:  # type: ignore
        member_data = member.dict(include={'id', 'first_name', 'last_name', 'email'})
        member_scheme = MemberSchemas.Member(**member_data)
        member_list.append(member_scheme)
    # Return the list of members
    return MemberSchemas.MemberList(members=member_list)


# Add groups/members to group
async def add_workspace_members(workspace: Workspace,
                                member_data: MemberSchemas.AddMembers) -> MemberSchemas.MemberList:
    accounts = set(member_data.accounts)
    # Remove existing members from the accounts set
    accounts = accounts.difference({member.id for member in workspace.members})  # type: ignore
    # Find the accounts from the database
    account_list = await Account.find(In(Account.id, accounts)).to_list()
    # Add the accounts to the group member list with basic permissions
    for account in account_list:
        await workspace.add_member(workspace, account, Permissions.WORKSPACE_BASIC_PERMISSIONS, save=False)
    await Workspace.save(workspace, link_rule=WriteRules.WRITE)
    # Return the list of members added to the group
    return MemberSchemas.MemberList(members=[MemberSchemas.Member(**account.dict()) for account in account_list])


# Remove a member from a workspace
async def remove_workspace_member(workspace: Workspace, account_id: ResourceID):
    # Check if account_id is specified in request, if account_id is not specified, use the current user
    if account_id:
        account = await Account.get(account_id)  # type: ignore
    else:
        account = current_active_user.get()
    # Check if the account exists
    if not account:
        raise AccountExceptions.AccountNotFound(account_id)
    # Check if the account is a member of the workspace
    if account.id not in [ResourceID(member.id) for member in workspace.members]:  # type: ignore
        raise WorkspaceExceptions.UserNotMember(workspace, account)
    # Remove the account from the workspace
    if await workspace.remove_member(account):
        # Return the list of members added to the group
        member_list = [MemberSchemas.Member(**account.dict()) for account in workspace.members]  # type: ignore
        return MemberSchemas.MemberList(members=member_list)
    raise WorkspaceExceptions.ErrorWhileRemovingMember(workspace, account)


# Get a list of groups where the account is a member
async def get_groups(workspace: Workspace) -> GroupSchemas.GroupList:
    # await workspace.fetch_link(Workspace.groups)
    account = current_active_user.get()
    group_list = []

    # Convert the list of links to a list of
    group: Group
    for group in workspace.groups:  # type: ignore
        member: Account
        for member in group.members:  # type: ignore
            if account.id == ResourceID(member.id):
                group_list.append(GroupSchemas.GroupShort(**group.dict()))
    # Return the list of groups
    return GroupSchemas.GroupList(groups=group_list)


# Create a new group with account as the owner
async def create_group(workspace: Workspace,
                       input_data: GroupSchemas.GroupCreateInput) -> GroupSchemas.GroupCreateOutput:
    # await workspace.fetch_link(workspace.groups)
    account = current_active_user.get()

    # Check if group name is unique
    group: Group  # For type hinting, until Link type is supported
    for group in workspace.groups:  # type: ignore
        if group.name == input_data.name:
            raise GroupExceptions.NonUniqueName(group)

    # Create a new group
    new_group = Group(name=input_data.name,
                      description=input_data.description,
                      workspace=workspace)  # type: ignore

    # Check if group was created
    if not new_group:
        raise GroupExceptions.ErrorWhileCreating(new_group)

    # Add the account to group member list
    await new_group.add_member(workspace, account, Permissions.GROUP_ALL_PERMISSIONS)

    # Create a policy for the new group
    permissions = Permissions.WORKSPACE_BASIC_PERMISSIONS  # type: ignore
    new_policy = Policy(policy_holder_type='group',
                        policy_holder=(await create_link(new_group)),
                        permissions=permissions,
                        workspace=workspace)  # type: ignore

    # Add the group and the policy to the workspace
    workspace.policies.append(new_policy)  # type: ignore
    workspace.groups.append(new_group)  # type: ignore
    await Workspace.save(workspace, link_rule=WriteRules.WRITE)

    # Return the new group
    return GroupSchemas.GroupCreateOutput(**new_group.dict())


# Get all policies of a workspace
async def get_workspace_policies(workspace: Workspace) -> PolicySchemas.PolicyList:
    policy_list = []
    policy: Policy
    for policy in workspace.policies:  # type: ignore
        permissions = Permissions.WorkspacePermissions(policy.permissions).name.split('|')  # type: ignore
        # Get policy_holder
        if policy.policy_holder_type == 'account':
            policy_holder = await Account.get(policy.policy_holder.ref.id)
        elif policy.policy_holder_type == 'group':
            policy_holder = await Group.get(policy.policy_holder.ref.id)
        else:
            raise GenericExceptions.InternalServerError(str("Unknown policy_holder_type"))
        if not policy_holder:
            # TODO: Replace with a custom exception
            raise AccountExceptions.AccountNotFound(policy.policy_holder.ref.id)
        # Convert the policy_holder to a Member schema
        policy_holder = MemberSchemas.Member(**policy_holder.dict())  # type: ignore
        policy_list.append(PolicySchemas.PolicyShort(id=policy.id,
                                                     policy_holder_type=policy.policy_holder_type,
                                                     # Exclude unset fields(i.e. "description" for Account)
                                                     policy_holder=policy_holder.dict(exclude_unset=True),
                                                     permissions=permissions))
    return PolicySchemas.PolicyList(policies=policy_list)


# List all permissions for a user in a workspace
async def get_workspace_policy(workspace: Workspace,
                               account_id: ResourceID | None = None) -> PolicySchemas.PolicyOutput:
    # Check if account_id is specified in request, if account_id is not specified, use the current user
    account: Account = await Account.get(account_id) if account_id else current_active_user.get()  # type: ignore

    if not account and account_id:
        raise AccountExceptions.AccountNotFound(account_id)

    # Check if account is a member of the workspace
    if account.id not in [member.id for member in workspace.members]:  # type: ignore
        raise WorkspaceExceptions.UserNotMember(workspace, account)

    user_permissions = await Permissions.get_all_permissions(workspace, account)
    return PolicySchemas.PolicyOutput(
        permissions=Permissions.WorkspacePermissions(user_permissions).name.split('|'),  # type: ignore
        policy_holder=MemberSchemas.Member(**account.dict()))


# Set permissions for a user in a workspace
async def set_workspace_policy(workspace: Workspace,
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
        # Make sure the account is loaded
        if not account:
            raise GenericExceptions.APIException(code=500, detail='Unknown error')  # Should not happen

        try:
            # Find the policy for the account
            p: Policy
            for p in workspace.policies:  # type: ignore
                if p.policy_holder_type == "account":
                    if p.policy_holder.ref.id == account.id:
                        policy = p
                        break
                # if not policy:
                #     policy = Policy(policy_holder_type='account',
                #                     policy_holder=(await create_link(account)),
                #                     permissions=Permissions.WorkspacePermissions(0),
                #                     workspace=workspace)
        except Exception as e:
            raise GenericExceptions.InternalServerError(str(e))

    # Calculate the new permission value from request
    new_permission_value = 0
    for i in input_data.permissions:
        try:
            new_permission_value += Permissions.WorkspacePermissions[i].value  # type: ignore
        except KeyError:
            raise GenericExceptions.InvalidPermission(i)
    # Update permissions
    policy.permissions = Permissions.WorkspacePermissions(new_permission_value)  # type: ignore
    await Policy.save(policy)

    # Get Account or Group from policy_holder link
    # HACK: Have to do it manualy, as Beanie cannot fetch policy_holder link of mixed types (Account | Group)
    if policy.policy_holder_type == "account":  # type: ignore
        policy_holder = await Account.get(policy.policy_holder.ref.id)  # type: ignore
    elif policy.policy_holder_type == "group":  # type: ignore
        policy_holder = await Group.get(policy.policy_holder.ref.id)  # type: ignore

    # Return the updated policy
    return PolicySchemas.PolicyOutput(
        permissions=Permissions.WorkspacePermissions(policy.permissions).name.split('|'),  # type: ignore
        policy_holder=MemberSchemas.Member(**policy_holder.dict()))  # type: ignore
