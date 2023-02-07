from app.models.user_manager import current_active_user
from app.models.workspace import Workspace
from app.schemas.workspace import (WorkspaceList, WorkspaceReadShort, WorkspaceReadFull)
from app.schemas.user import UserRead


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
