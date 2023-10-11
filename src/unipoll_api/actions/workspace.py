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
    policies = (await actions.PolicyActions.get_policies(resource=workspace)).policies if include_policies else None
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
