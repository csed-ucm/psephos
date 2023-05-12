# from typing import Optional
# from pydantic import EmailStr
from beanie import WriteRules
from beanie.operators import In
from app.account_manager import current_active_user
from app.models.documents import Group, ResourceID, Workspace, Account, Policy, create_link
from app.schemas import workspace as WorkspaceSchemas
from app.schemas import account as AccountSchemas
from app.schemas import group as GroupSchemas
from app.schemas import policy as PolicySchemas
from app.exceptions import workspace as WorkspaceExceptions
from app.exceptions import account as AccountExceptions
from app.exceptions import group as GroupExceptions
from app.exceptions import resource as GenericExceptions
from app.utils import permissions as Permissions


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
    new_workspace = Workspace(name=input_data.name,
                              description=input_data.description)

    # Check if workspace was created
    if not new_workspace:
        raise WorkspaceExceptions.ErrorWhileCreating(input_data.name)    

    # Create a policy for the new member
    # New member has full permissions on the workspace
    full_permissions = Permissions.WorkspacePermissions(-1)
    new_policy = Policy(policy_holder_type='account',
                        policy_holder=(await create_link(account)),
                        permissions=full_permissions,
                        workspace=new_workspace)

    # Add the current user and the policy to workspace member list
    new_workspace.members.append(account)
    new_workspace.policies.append(new_policy)
    await Workspace.save(new_workspace, link_rule=WriteRules.WRITE)

    # Specify fields for output schema
    return WorkspaceSchemas.WorkspaceCreateOutput(**new_workspace.dict())


# Get a workspace
async def get_workspace(workspace: Workspace) -> WorkspaceSchemas.Workspace:
    await workspace.fetch_all_links()
    return WorkspaceSchemas.WorkspaceShort(**workspace.dict())


# Update a workspace
async def update_workspace(workspace: Workspace, input_data: WorkspaceSchemas.WorkspaceCreateInput):
    if workspace.name != input_data.name or workspace.description != input_data.description:
        if await Workspace.find_one({"name": input_data.name}) and workspace.name != input_data.name:
            raise WorkspaceExceptions.NonUniqueName(input_data.name)
        workspace.name = input_data.name
        workspace.description = input_data.description
        await Workspace.save(workspace)
    return WorkspaceSchemas.WorkspaceShort(**workspace.dict())


# Delete a workspace
async def delete_workspace(workspace: Workspace):
    await workspace.delete()  # type: ignore
    if await workspace.get(workspace.id):
        raise WorkspaceExceptions.ErrorWhileDeleting(workspace.id)
    else:
        return {'message': 'Workspace deleted successfully'}


# List all members of a workspace
async def get_workspace_members(workspace: Workspace):
    await workspace.fetch_link(Workspace.members)
    member_list = []
    member: Account
    # NOTE: The type test cannot check the type of the link, so we ignore it
    for member in workspace.members:  # type: ignore
        member_data = member.dict(
            include={'id', 'first_name', 'last_name', 'email'})
        member_scheme = AccountSchemas.Account(**member_data)
        member_list.append(member_scheme)

    # # Return the list of members
    return {'members': member_list}


# Add groups/members to group
async def add_workspace_members(workspace: Workspace, member_data: WorkspaceSchemas.AddMembers):
    accounts = set(member_data.accounts)

    # Remove existing members from the accounts set
    accounts = accounts.difference({member.ref.id for member in workspace.members})

    # Find the accounts from the database
    account_list = await Account.find(In(Account.id, accounts)).to_list()

    # Default policy(permissions) for the new members
    default_permissions: Permissions.GroupPermissions = Permissions.GroupPermissions(1)  # type: ignore

    # Add the accounts to the group member list with default permissions
    for account in account_list:
        await workspace.add_member(workspace.workspace, account, default_permissions)
    await workspace.save(workspace)

    return {"new members": [AccountSchemas.AccountShort(**account.dict()) for account in account_list]}


# Remove a member from a workspace
async def remove_workspace_member(workspace: Workspace, account_id: ResourceID):
    account = await Account.get(account_id)
    if not account:
        raise AccountExceptions.AccountNotFound(account_id)

    if account.id not in [ResourceID(member.ref.id) for member in workspace.members]:
        raise WorkspaceExceptions.UserNotMember(workspace, account)
    return await workspace.remove_member(account)


# Get a list of groups where the account is a member
async def get_groups(workspace: Workspace) -> GroupSchemas.GroupList:
    await workspace.fetch_link(Workspace.groups)
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
    await workspace.fetch_link(Workspace.groups)
    group: Group  # For type hinting, until Link type is supported
    for group in workspace.groups:  # type: ignore
        if group.name == input_data.name:
            raise GroupExceptions.NonUniqueName(group)

    # Create a new group
    new_group = Group(name=input_data.name,
                      description=input_data.description,
                      workspace=workspace)

    # Check if group was created
    if not new_group:
        raise GroupExceptions.ErrorWhileCreating(new_group)

    # Add the account to group member list
    await new_group.add_member(workspace, account, Permissions.GroupPermissions(-1))

    # Create a policy for the new group
    full_permissions = Permissions.WorkspacePermissions(-1)  # type: ignore
    new_policy = Policy(policy_holder_type='group',
                        policy_holder=(await create_link(new_group)),
                        permissions=full_permissions,
                        workspace=workspace)

    # Add the group and the policy to the workspace
    workspace.policies.append(new_policy)
    workspace.groups.append(new_group)
    await Workspace.save(workspace, link_rule=WriteRules.WRITE)

    # Return the new group
    return GroupSchemas.GroupCreateOutput(**new_group.dict())


# List all permissions for a user in a workspace
async def get_workspace_permissions(workspace: Workspace, account_id: ResourceID | None):
    # Check if account_id is specified in request, if account_id is not specified, use the current user
    account: Account = await Account.get(account_id) if account_id else current_active_user.get()  # type: ignore

    if not account:
        raise AccountExceptions.AccountNotFound(account_id)

    # Check if account is a member of the workspace
    if account.id not in [member.ref.id for member in workspace.members]:
        raise WorkspaceExceptions.UserNotMember(workspace, account)

    await workspace.fetch_link(Workspace.policies)
    user_permissions = await Permissions.get_all_permissions(workspace, account)
    res = {
        'permissions': Permissions.WorkspacePermissions(user_permissions).name.split('|'),  # type: ignore
        'account': AccountSchemas.Account(**account.dict())
        }
    return res


# Set permissions for a user in a workspace
async def get_all_workspace_policies(workspace: Workspace):
    policy_list = []
    await workspace.fetch_link(workspace.policies)
    for policy in workspace.policies:
        policy_list.append(PolicySchemas.Policy(**policy.dict()))  # type: ignore
    return {"policies": policy_list}


async def set_workspace_permissions(workspace: Workspace, input_data: PolicySchemas.PolicyInput):
    account: Account = current_active_user.get()
    await workspace.fetch_link(workspace.policies)
    # Find the policy for the account
    policy: Policy
    for policy in workspace.policies:  # type: ignore
        if policy.policy_holder == account:
            new_permission_value = 0
            for i in input_data.permissions:
                try:
                    new_permission_value += Permissions.WorkspacePermissions[i].value  # type: ignore
                except KeyError:
                    raise GenericExceptions.InvalidPermission(i)
            policy.permissions = Permissions.WorkspacePermissions(new_permission_value)  # type: ignore
            await Policy.save(policy)
            return {'permissions': Permissions.WorkspacePermissions(policy.permissions).name.split('|')}  # type: ignore
    raise WorkspaceExceptions.UserNotMember(workspace, account)
