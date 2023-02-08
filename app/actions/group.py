
from app.models.workspace import Workspace
from app.models.group import Group
# from app.models.user import User
from app.models.user_manager import current_active_user
from app.schemas.user import UserReadShort
from app.schemas.group import (GroupReadShort, GroupReadFull, GroupList)


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
    group_list = []
    search_result = await Group.find({'members': user}).to_list()

    # Create a group list for output schema using the search results
    for group in search_result:
        group_list.append(GroupReadShort(name=group.name, description=group.description))

    return GroupList(groups=group_list)
