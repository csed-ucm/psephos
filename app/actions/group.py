from beanie import DeleteRules
from beanie.operators import In
# from devtools import debug
from app.models.workspace import Workspace
from app.models.group import Group
from app.models.user import User
from app.models.user_manager import current_active_user
from app.models.policy import Policy
from app.schemas.user import UserID, UserReadShort
from app.schemas import group as GroupSchemas
# from app.schemas.workspace import WorkspaceID
from app.exceptions import group as GroupExceptions
from app.exceptions import user as UserExceptions
from app.exceptions import workspace as WorkspaceExceptions
from app.mongo_db import create_link
from app.utils import colored_dbg
from app.utils.permissions import GroupPermissions


# Get all groups
async def get_all_groups() -> GroupSchemas.GroupList:
    group_list = []
    search_result = await Group.find_all().to_list()

    # Create a group list for output schema using the search results
    for group in search_result:
        await group.fetch_link(Group.owner)
        # NOTE: The type test cannot check the type of the link, so we ignore it
        owner_data = group.owner.dict(  # type: ignore
            include={'id', 'first_name', 'last_name', 'email'})
        owner_scheme = UserReadShort(**owner_data)
        group_list.append(GroupSchemas.GroupReadFull(
            name=group.name,
            description=group.description,
            owner=owner_scheme,
            members_count=len(group.members)))

    return GroupSchemas.GroupList(groups=group_list)


# Get a list of groups where the user is a owner/member
async def get_user_groups(workspace: Workspace) -> GroupSchemas.GroupList:
    await workspace.fetch_link(Workspace.groups)
    user = current_active_user.get()
    group_list: list[GroupSchemas.GroupReadShort] = []

    # Convert the list of links to a list of
    group: Group
    for group in workspace.groups:  # type: ignore
        member: User
        for member in group.members:   # type: ignore
            # if user.id == UserID(member.ref.id):
            if user.id == UserID(member.id):
                group_list.append(GroupSchemas.GroupReadShort(
                    name=group.name, description=group.description))

    # Return the list of groups
    return GroupSchemas.GroupList(groups=group_list)


# Create a new group with user as the owner
async def create_group(workspace: Workspace,
                       input_data: GroupSchemas.GroupCreateInput) -> GroupSchemas.GroupCreateOutput:
    # await workspace.fetch_link(workspace.groups)
    user = current_active_user.get()

    # Check if group name is unique
    await workspace.fetch_link(Workspace.groups)
    group: Group  # For type hinting, until Link type is supported
    for group in workspace.groups:  # type: ignore
        if group.name == input_data.name:
            raise GroupExceptions.NonUniqueName(group)

    # Create a new group
    # workspace_link = await create_link(workspace)
    new_group = await Group(name=input_data.name,
                            description=input_data.description,
                            owner=user,
                            workspace=workspace.id).create()

    # Check if group was created
    if not new_group:
        raise GroupExceptions.ErrorWhileCreating(new_group)

    # Add the user to group member list
    await new_group.add_member(user)

    # Add the group to workspace group list
    workspace.groups.append(await create_link(new_group))
    await Workspace.save(workspace)

    # Specify fields for output schema
    result = new_group.dict(include={'id': True,
                                     'name': True,
                                     'description': True,
                                     'owner': {'id', 'first_name', 'last_name', 'email'}})

    return GroupSchemas.GroupCreateOutput(**result)


# Get group by id
async def get_group(group: Group) -> GroupSchemas.GroupReadFull:
    # Fetch the owner of the group
    await group.fetch_link(Group.owner)

    # NOTE: The type test cannot check the type of the link, so we ignore it
    owner_data = group.owner.dict(  # type: ignore
        include={'id', 'first_name', 'last_name', 'email'})
    owner_scheme = UserReadShort(**owner_data)

    # Create a group list for output schema using the search results
    group_list = GroupSchemas.GroupReadFull(
        name=group.name,
        description=group.description,
        owner=owner_scheme,
        members_count=len(group.members))

    return group_list


# Update a group
async def update_group(group: Group, group_data: GroupSchemas.GroupUpdateIn) -> GroupSchemas.GroupReadShort:
    # Check if group name is unique
    workspace = await Workspace.get(group.workspace)
    if not workspace:
        raise WorkspaceExceptions.WorkspaceNotFound(group.workspace)

    # Check if there is any data to update
    if not group_data.name and not group_data.description:
        return GroupSchemas.GroupReadShort(name=group.name, description=group.description)
        # Raise an exception

    # Update the group
    if group_data.name:
        # Check if group name is unique
        await workspace.fetch_link(Workspace.groups)
        for _group in workspace.groups:
            if _group.name == group_data.name:  # type: ignore
                raise GroupExceptions.NonUniqueName(group)
        group.name = group_data.name  # Update the group name
    if group_data.description:
        group.description = group_data.description  # Update the group description

    # Save the updates
    await Group.save(group)
    return GroupSchemas.GroupReadShort(name=group.name, description=group.description)


# Delete a group
async def delete_group(group: Group):
    # await Group.delete(group) # link_rule=DeleteRules.DELETE_LINKS
    await Group.delete(group, link_rule=DeleteRules.DELETE_LINKS)

    workspace = await Workspace.get(group.workspace)
    if workspace:
        workspace.groups = [g for g in workspace.groups if g.ref.id != group.id]
        await Workspace.save(workspace)

    if await Group.get(group.id):
        return GroupExceptions.ErrorWhileDeleting(group.id)


# Add a single member to group
async def add_member(group: Group, user_id: UserID):
    user = await User.get(user_id)
    if not user:
        raise UserExceptions.UserNotFound(user_id)

    workspace = await Workspace.get(group.workspace)
    if not workspace:
        raise WorkspaceExceptions.WorkspaceNotFound(group.workspace)

    # Check if user is already a member
    if user.id in [UserID(member.ref.id) for member in group.members]:
        raise GroupExceptions.AddingExistingMember(group, user)
    # Check if user is a member of the workspace
    if user.id not in [UserID(member.ref.id) for member in workspace.members]:
        raise WorkspaceExceptions.UserNotMember(workspace, user)

    # TODO: Create a member object and add it to the group instead of adding the user directly
    link = await create_link(user)
    group.members.append(link)
    colored_dbg.info(
        f'User {user.id} has been added to workspace {workspace.id} as a member.')
    await Workspace.save(workspace)
    return user


# Get list of members of a group
async def get_members(group: Group) -> list[UserReadShort]:
    await group.fetch_link(Group.members)
    attributes = {'id', 'first_name', 'last_name', 'email'}
    members = [member.dict(include=attributes) for member in group.members]  # type: ignore
    member_list = [UserReadShort(**member) for member in members]
    return member_list


# Add groups/members to group
async def add_members(group: Group, member_data: GroupSchemas.AddMembers):
    accounts = set()  # A set to store unique ids of user accounts

    # Find existing groups from the member_data
    group_list = await Group.find(In(Group.id, member_data.groups)).to_list()  # fetch_links=True
    # Add the members of each group to the accounts set
    for group_to_add in group_list:
        for account in group_to_add.members:
            accounts.add(account.ref.id)

    # Find existing users from the member_data
    accounts.update(member_data.accounts)
    accounts = accounts.difference({member.ref.id for member in group.members})
    user_list = await User.find(In(User.id, member_data.groups)).to_list()

    print(user_list)
    # Add the user accounts to the group member list
    group.members.extend([await create_link(account) for account in user_list])
    await Group.save(group)


# Link a group from the same workspace to another group to access its members
async def link_group(group: Group, workspace: Workspace):
    # Add group/s to the list
    group.linked_groups.append(await create_link(group))
    await Group.save(group)


async def add_permission(group: Group, member_data: GroupSchemas.AddPermission):
    # Find existing groups from the member_data
    group_list = await Group.find(In(Group.id, member_data.permissions)).to_list()  # fetch_links=True
    for new_group in group_list:
        group_link = await create_link(new_group)
        new_policy = await Policy(policy_holder_type="Group", 
                                  policy_holder=link,
                                  permissions=GroupPermissions['get_group_info']).create()
        