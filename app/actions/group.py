
from app.models.workspace import Workspace
from app.models.group import Group
# from app.models.user import User
from app.models.user_manager import current_active_user
from app.schemas.user import UserID, UserReadShort
from app.schemas.group import (GroupReadShort, GroupReadFull, GroupList, GroupCreateInput, GroupCreateOutput)
from app.exceptions import group as GroupExceptions
from app.mongo_db import create_link


# Get all groups
async def get_all_groups() -> GroupList:
    group_list = []
    search_result = await Group.find_all().to_list()

    # Create a group list for output schema using the search results
    for group in search_result:
        await group.fetch_link(Group.owner)
        # NOTE: The type test cannot check the type of the link, so we ignore it
        owner_data = group.owner.dict(  # type: ignore
            include={'id', 'first_name', 'last_name', 'email'})
        owner_scheme = UserReadShort(**owner_data)
        group_list.append(GroupReadFull(
            name=group.name,
            description=group.description,
            owner=owner_scheme,
            members_count=len(group.members)))

    return GroupList(groups=group_list)


# Get a list of groups where the user is a owner/member
async def get_user_groups(workspace: Workspace) -> GroupList:
    await workspace.fetch_link(Workspace.groups)
    user = current_active_user.get()
    group_list: list[GroupReadShort] = []
    # Convert the list of links to a list of
    group: Group
    for group in workspace.groups:  # type: ignore
        for member in group.members:
            if user.id == UserID(member.ref.id):
                group_list.append(GroupReadShort(name=group.name, description=group.description))
    # Return the list of groups
    return GroupList(groups=group_list)


# Create a new group with user as the owner
async def create_group(workspace: Workspace, input_data: GroupCreateInput) -> GroupCreateOutput:
    # await workspace.fetch_link(workspace.groups)
    user = current_active_user.get()

    print(input_data)

    # Check if group name is unique
    if await Group.find_one({"name": input_data.name}):
        raise GroupExceptions.NonUniqueName(input_data.name)

    # Create a new group
    new_group = await Group(name=input_data.name,
                            description=input_data.description,
                            owner=user).create()

    # Check if group was created
    if not new_group:
        raise GroupExceptions.ErrorWhileCreating(input_data.name)

    # Add the user to group member list
    await new_group.add_member(user)

    # TODO: Check if member was added
    
    workspace.groups.append(await create_link(new_group))
    await workspace.save()

    # Specify fields for output schema
    result = new_group.dict(include={'id': True,
                                     'name': True,
                                     'description': True,
                                     'owner': {'id', 'first_name', 'last_name', 'email'}})

    return GroupCreateOutput(**result)
