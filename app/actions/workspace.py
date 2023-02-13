from app.models.user_manager import current_active_user
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import (WorkspaceList, WorkspaceReadShort, WorkspaceReadFull,
                                   WorkspaceCreateInput, WorkspaceCreateOutput)
from app.schemas.user import UserID, UserReadShort, UserReadFull
# from app.models.user import User
from app.exceptions import workspace as WorkspaceExceptions
from app.exceptions import user as UserExceptions


# Get all workspaces
async def get_all_workspaces() -> WorkspaceList:
    workspace_list = []
    search_result = await Workspace.find_all().to_list()

    # Create a workspace list for output schema using the search results
    for workspace in search_result:
        await workspace.fetch_link(Workspace.owner)
        # NOTE: The type test cannot check the type of the link, so we ignore it
        owner_data = workspace.owner.dict(  # type: ignore
            include={'id', 'first_name', 'last_name', 'email'})
        owner_scheme = UserReadShort(**owner_data)
        workspace_list.append(WorkspaceReadFull(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
            owner=owner_scheme,
            members_count=len(workspace.members)))

    return WorkspaceList(workspaces=workspace_list)


# Get a list of workspaces where the user is a owner/member
async def get_user_workspaces() -> WorkspaceList:
    user = current_active_user.get()
    workspace_list = []
    search_result = await Workspace.find(Workspace.members.id == user.id).to_list()  # type: ignore

    # Create a workspace list for output schema using the search results
    for workspace in search_result:
        await workspace.fetch_link(Workspace.owner)
        owner = workspace.owner == user  # Check if user is the owner
        workspace_list.append(WorkspaceReadShort(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
            owner=owner))

    return WorkspaceList(workspaces=workspace_list)


# Create a new workspace with user as the owner
async def create_workspace(input_data: WorkspaceCreateInput) -> WorkspaceCreateOutput:
    user = current_active_user.get()

    # Check if workspace name is unique
    if await Workspace.find_one({"name": input_data.name}):
        raise WorkspaceExceptions.NonUniqueName(input_data.name)

    # Create a new workspace
    new_workspace = await Workspace(name=input_data.name,
                                    description=input_data.description,
                                    owner=user).create()

    # Check if workspace was created
    if not new_workspace:
        raise WorkspaceExceptions.ErrorWhileCreating(input_data.name)

    # Add the user to workspace member list
    await new_workspace.add_member(user)

    # Specify fields for output schema
    result = new_workspace.dict(include={'id': True,
                                         'name': True,
                                         'description': True,
                                         'owner': {'id', 'first_name', 'last_name', 'email'}})

    return WorkspaceCreateOutput(**result)


# List all members of a workspace
async def get_members(workspace: Workspace):
    await workspace.fetch_link(Workspace.members)
    member_list = []
    member: User
    # NOTE: The type test cannot check the type of the link, so we ignore it
    for member in workspace.members:  # type: ignore
        member_data = member.dict(include={'id', 'first_name', 'last_name', 'email'})
        member_scheme = UserReadShort(**member_data)
        print(member_scheme)
        member_list.append(member_scheme)

    # Return the list of members
    return member_list


# Add a member to a workspace
async def add_member(workspace: Workspace, user_id: UserID):
    user = await User.get(user_id)
    if user:
        return await workspace.add_member(user)
    else:
        raise UserExceptions.UserNotFound(user_id)
