from app.models.user_manager import current_active_user
from app.models.workspace import Workspace
from app.schemas.workspace import (WorkspaceList, WorkspaceReadShort, WorkspaceReadFull,
                                   WorkspaceCreateInput, WorkspaceCreateOutput)
from app.schemas.user import UserRead
# from app.models.user import User
from app.exceptions import workspace as workspace_exceptions


# Get all workspaces
async def get_all_workspaces() -> WorkspaceList:
    workspace_list = []
    search_result = await Workspace.find_all(fetch_links=True).to_list()

    # Create a workspace list for output schema using the search results
    for workspace in search_result:
        # NOTE: The type test cannot check the type of the link, so we ignore it
        owner_data = workspace.owner.dict(  # type: ignore
            include={'id', 'first_name', 'last_name', 'email'})
        owner_scheme = UserRead(**owner_data)
        workspace_list.append(WorkspaceReadFull(
            name=workspace.name, description=workspace.description, owner=owner_scheme))

    return WorkspaceList(workspaces=workspace_list)


# Get a list of workspaces where the user is a owner/member
async def get_user_workspaces() -> WorkspaceList:
    user = current_active_user.get()
    workspace_list = []
    search_result = await Workspace.find({'members': user}, fetch_links=True).to_list()

    # Create a workspace list for output schema using the search results
    for workspace in search_result:
        owner = workspace.owner == user  # Check if user is the owner
        workspace_list.append(WorkspaceReadShort(
            name=workspace.name, description=workspace.description, owner=owner))

    return WorkspaceList(workspaces=workspace_list)


# Create a new workspace with user as the owner
async def create_workspace(input_data: WorkspaceCreateInput) -> WorkspaceCreateOutput:
    user = current_active_user.get()

    # Check if workspace name is unique
    if await Workspace.find_one({"name": input_data.name}):
        raise workspace_exceptions.ExistsWithSuchName(input_data.name)

    # Create a new workspace
    new_workspace = await Workspace(name=input_data.name,
                                    description=input_data.description,
                                    owner=user).create()

    # Check if workspace was created
    if not new_workspace:
        raise workspace_exceptions.ErrorWhileCreating(input_data.name)

    # Add the user to workspace member list
    await new_workspace.add_member(user)

    # Specify fields for output schema
    result = new_workspace.dict(include={'id': True,
                                         'name': True,
                                         'description': True,
                                         'owner': {'id', 'first_name', 'last_name', 'email'}})

    return WorkspaceCreateOutput(**result)
