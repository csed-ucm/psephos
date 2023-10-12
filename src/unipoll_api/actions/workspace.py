from unipoll_api import AccountManager
from unipoll_api import actions
from unipoll_api.documents import Workspace, Account, Policy
from unipoll_api.utils import Permissions
from unipoll_api.schemas import WorkspaceSchemas
from unipoll_api.exceptions import WorkspaceExceptions


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

    await new_workspace.add_member(account=account, permissions=Permissions.WORKSPACE_ALL_PERMISSIONS)

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
    polls = (await actions.PollActions.get_polls(workspace)).polls if include_polls else None
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
    # BUG: Cannot delete groups
    for group in workspace.groups:
        await actions.GroupActions.delete_group(group)  # type: ignore

    await Workspace.delete(workspace)
    if await workspace.get(workspace.id):
        raise WorkspaceExceptions.ErrorWhileDeleting(workspace.id)
    await Policy.find({"parent_resource._id": workspace.id}, fetch_links=True).delete()
