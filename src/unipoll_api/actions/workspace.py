# from typing import Optional
# from pydantic import EmailStr
from beanie import WriteRules, DeleteRules
from unipoll_api import AccountManager
from unipoll_api import actions
from unipoll_api.documents import Group, ResourceID, Workspace, Account, Policy, Poll
from unipoll_api.utils import Permissions
from unipoll_api.schemas import WorkspaceSchemas, PolicySchemas, MemberSchemas, PollSchemas
from unipoll_api.exceptions import (WorkspaceExceptions, AccountExceptions, ResourceExceptions,
                                    PolicyExceptions, PollExceptions)


# Get a list of workspaces where the account is a owner/member
async def get_workspaces(account: Account | None = None) -> WorkspaceSchemas.WorkspaceList:
    account = AccountManager.active_user.get()
    workspace_list = []

    search_result = await Workspace.find(Workspace.members.id == account.id).to_list()  # type: ignore

    # Create a workspace list for output schema using the search results
    for workspace in search_result:
        workspace_list.append(WorkspaceSchemas.WorkspaceShort(
            **workspace.model_dump(exclude={'members', 'groups', 'permissions'})))

    return WorkspaceSchemas.WorkspaceList(workspaces=workspace_list)


# Create a new workspace with account as the owner
async def create_workspace(input_data: WorkspaceSchemas.WorkspaceCreateInput) -> WorkspaceSchemas.WorkspaceCreateOutput:
    account: Account = AccountManager.active_user.get()
    # Check if workspace name is unique
    if await Workspace.find_one({"name": input_data.name}):
        raise WorkspaceExceptions.NonUniqueName(input_data.name)

    # Create a new workspace
    new_workspace = await Workspace(name=input_data.name, description=input_data.description).create()

    # Check if workspace was created
    if not new_workspace:
        raise WorkspaceExceptions.ErrorWhileCreating(input_data.name)

    await new_workspace.add_member(account=account, permissions=Permissions.WORKSPACE_ALL_PERMISSIONS, save=False)
    await Workspace.save(new_workspace, link_rule=WriteRules.WRITE)

    # Specify fields for output schema
    return WorkspaceSchemas.WorkspaceCreateOutput(**new_workspace.model_dump(include={'id', 'name', 'description'}))


# Get a workspace
async def get_workspace(workspace: Workspace,
                        include_groups: bool = False,
                        include_policies: bool = False,
                        include_members: bool = False,
                        include_polls: bool = False) -> WorkspaceSchemas.Workspace:
    groups = (await actions.GroupActions.get_groups(workspace)).groups if include_groups else None
    members = (await actions.MembersActions.get_members(workspace)).members if include_members else None
    policies = (await get_workspace_policies(workspace)).policies if include_policies else None
    polls = (await get_polls(workspace)).polls if include_polls else None
    # Return the workspace with the fetched resources
    return WorkspaceSchemas.Workspace(id=workspace.id,
                                      name=workspace.name,
                                      description=workspace.description,
                                      groups=groups,
                                      members=members,
                                      policies=policies,
                                      polls=polls)


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
    return WorkspaceSchemas.Workspace(**workspace.model_dump())


# Delete a workspace
async def delete_workspace(workspace: Workspace):
    await Workspace.delete(workspace, link_rule=DeleteRules.DO_NOTHING)
    # await Workspace.delete(workspace, link_rule=DeleteRules.DELETE_LINKS)
    if await workspace.get(workspace.id):
        raise WorkspaceExceptions.ErrorWhileDeleting(workspace.id)
    await Policy.find(Policy.parent_resource.id == workspace.id).delete()  # type: ignore
    await Group.find(Group.workspace.id == workspace).delete()  # type: ignore





# Get all policies of a workspace
async def get_workspace_policies(workspace: Workspace) -> PolicySchemas.PolicyList:
    policy_list = await actions.PolicyActions.get_policies(resource=workspace)

    return PolicySchemas.PolicyList(policies=policy_list.policies)


# Get a policy of a workspace
async def get_workspace_policy(workspace: Workspace,
                               account_id: ResourceID | None = None) -> PolicySchemas.PolicyOutput:
    # Check if account_id is specified in request, if account_id is not specified, use the current user
    account: Account = await Account.get(account_id) if account_id else AccountManager.active_user.get()  # type: ignore
    policy_list = await actions.PolicyActions.get_policies(resource=workspace, policy_holder=account)
    user_policy = policy_list.policies[0]

    return PolicySchemas.PolicyOutput(
        permissions=user_policy.permissions,  # type: ignore
        policy_holder=user_policy.policy_holder)


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
            account = AccountManager.active_user.get()
        # Make sure the account is loaded
        if not account:
            raise ResourceExceptions.APIException(code=500, detail='Unknown error')  # Should not happen

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
            raise ResourceExceptions.InternalServerError(str(e))

    # Calculate the new permission value from request
    new_permission_value = 0
    for i in input_data.permissions:
        try:
            new_permission_value += Permissions.WorkspacePermissions[i].value  # type: ignore
        except KeyError:
            raise ResourceExceptions.InvalidPermission(i)
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
        policy_holder=MemberSchemas.Member(**policy_holder.model_dump()))  # type: ignore


# Get a list of polls in a workspace
async def get_polls(workspace: Workspace) -> PollSchemas.PollList:
    return await actions.PollActions.get_polls(workspace)


# Create a new poll in a workspace
async def create_poll(workspace: Workspace, input_data: PollSchemas.CreatePollRequest) -> PollSchemas.PollResponse:
    # Check if poll name is unique
    poll: Poll  # For type hinting, until Link type is supported
    for poll in workspace.polls:  # type: ignore
        if poll.name == input_data.name:
            raise PollExceptions.NonUniqueName(poll)

    # Create a new poll
    new_poll = Poll(name=input_data.name,
                    description=input_data.description,
                    workspace=workspace,  # type: ignore
                    public=input_data.public,
                    published=input_data.published,
                    questions=input_data.questions,
                    policies=[])

    # Check if poll was created
    if not new_poll:
        raise PollExceptions.ErrorWhileCreating(new_poll)

    # Add the poll to the workspace
    workspace.polls.append(new_poll)  # type: ignore
    await Workspace.save(workspace, link_rule=WriteRules.WRITE)

    # Return the new poll
    return PollSchemas.PollResponse(**new_poll.model_dump())
