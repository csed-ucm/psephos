# from typing import Optional
from pydantic import EmailStr

from app.models.user_manager import current_active_user
from app.models.user import User
# from app.models.group import Group
from app.models.workspace import Workspace
from app.mongo_db import create_link

from app.schemas.workspace import (WorkspaceList, WorkspaceReadShort, WorkspaceReadFull,
                                   WorkspaceCreateInput, WorkspaceCreateOutput)
from app.schemas.user import UserID, UserReadShort

from app.exceptions import workspace as WorkspaceExceptions
from app.exceptions import user as UserExceptions
from app.utils import colored_dbg


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


# Get a workspace
async def get_workspace(workspace: Workspace) -> WorkspaceReadFull:
    await workspace.fetch_link(Workspace.owner)
    owner: User = workspace.owner  # type: ignore
    owner_scheme = UserReadShort(id=owner.id,
                                 first_name=owner.first_name,
                                 last_name=owner.last_name,
                                 # NOTE: Replace str with EmailStr in User model
                                 email=EmailStr(owner.email))
    return WorkspaceReadFull(id=workspace.id,
                             name=workspace.name,
                             description=workspace.description,
                             owner=owner_scheme,
                             members_count=len(workspace.members))


# Update a workspace
async def update_workspace(workspace: Workspace, input_data: WorkspaceCreateInput):
    # TODO: Check if user has permission to update the workspace
    if workspace.name != input_data.name or workspace.description != input_data.description:
        if await Workspace.find_one({"name": input_data.name}) and workspace.name != input_data.name:
            raise WorkspaceExceptions.NonUniqueName(input_data.name)
        workspace.name = input_data.name
        workspace.description = input_data.description
        await Workspace.save(workspace)
    return WorkspaceReadShort(id=workspace.id,
                              name=workspace.name,
                              description=workspace.description,
                              owner=True)


# Delete a workspace
async def delete_workspace(workspace: Workspace):
    await workspace.delete()  # type: ignore
    if await workspace.get(workspace.id):
        raise WorkspaceExceptions.ErrorWhileDeleting(workspace.id)
    else:
        return {'message': 'Workspace deleted successfully'}


# List all members of a workspace
async def get_members(workspace: Workspace):
    await workspace.fetch_link(Workspace.members)
    member_list = []
    member: User
    # NOTE: The type test cannot check the type of the link, so we ignore it
    for member in workspace.members:  # type: ignore
        member_data = member.dict(
            include={'id', 'first_name', 'last_name', 'email'})
        member_scheme = UserReadShort(**member_data)
        member_list.append(member_scheme)

    # # Return the list of members
    return {'members': member_list}


# Add a member to a workspace
async def add_member(workspace: Workspace, user_id: UserID):
    user = await User.get(user_id)
    if not user:
        raise UserExceptions.UserNotFound(user_id)

    if user.id in [UserID(member.ref.id) for member in workspace.members]:
        raise WorkspaceExceptions.AddingExistingMember(workspace, user)

    link = await create_link(user)
    workspace.members.append(link)
    colored_dbg.info(
        f'User {user.id} has been added to workspace {workspace.id} as a member.')
    await Workspace.save(workspace)
    return user


# Remove a member from a workspace
async def remove_member(workspace: Workspace, user_id: UserID):
    user = await User.get(user_id)
    if not user:
        raise UserExceptions.UserNotFound(user_id)

    if user.id not in [UserID(member.ref.id) for member in workspace.members]:
        raise WorkspaceExceptions.UserNotMember(workspace, user)
    return await workspace.remove_member(user)
