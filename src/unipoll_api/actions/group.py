from beanie import WriteRules
from beanie.operators import Or
from bson import DBRef

from unipoll_api import AccountManager
from unipoll_api.documents import Policy, Workspace, Group, Account
from unipoll_api import actions
from unipoll_api.schemas import GroupSchemas, WorkspaceSchemas
from unipoll_api.exceptions import GroupExceptions, WorkspaceExceptions, ResourceExceptions
from unipoll_api.utils import Permissions
from unipoll_api.dependencies import get_member


# Get list of groups
async def get_groups(workspace: Workspace | None = None,
                     account: Account | None = None,
                     name: str | None = None) -> GroupSchemas.GroupList:
    account = account or AccountManager.active_user.get()

    search_filter = {}
    if name:
        search_filter['name'] = name  # type: ignore
    if workspace:
        search_filter['workspace._id'] = workspace.id  # type: ignore
    if account:
        search_filter['members.account._id'] = account.id  # type: ignore
    search_result = await Group.find(search_filter, fetch_links=True).to_list()

    # TODO: Rewrite to iterate over list of workspaces
    # TODO: to avoid permission check for every group if the user has permission to get all groups

    groups = []
    for group in search_result:
        try:
            groups.append((await get_group(group=group)).model_dump(exclude_none=True))
        except Exception:
            pass

    return GroupSchemas.GroupList(groups=groups)


# Create a new group with account as the owner
async def create_group(workspace: Workspace,
                       name: str,
                       description: str,
                       check_permissions: bool = True) -> GroupSchemas.GroupCreateOutput:

    await Permissions.check_permissions(workspace, "add_groups", check_permissions)
    account = AccountManager.active_user.get()

    member = await get_member(account, workspace)

    # Check if group name is unique
    group: Group  # For type hinting, until Link type is supported
    for group in workspace.groups:  # type: ignore
        if group.name == name:
            raise GroupExceptions.NonUniqueName(group)

    # Create a new group
    new_group = Group(name=name,
                      description=description,
                      workspace=workspace)  # type: ignore

    # Check if group was created
    if not new_group:
        raise GroupExceptions.ErrorWhileCreating(new_group)

    # Add the account to group member list
    await new_group.add_member(member, Permissions.GROUP_ALL_PERMISSIONS)

    # Create a policy for the new group
    await workspace.add_policy(new_group, Permissions.WORKSPACE_BASIC_PERMISSIONS, False)
    workspace.groups.append(new_group)  # type: ignore
    await Workspace.save(workspace, link_rule=WriteRules.WRITE)

    # Return the new group
    return GroupSchemas.GroupCreateOutput(**new_group.model_dump(include={'id', 'name', 'description'}))


# Get group
async def get_group(group: Group,
                    include_members: bool = False,
                    include_policies: bool = False,
                    check_permissions: bool = True) -> GroupSchemas.Group:
    try:
        await Permissions.check_permissions(group.workspace, "get_groups", check_permissions)
    except ResourceExceptions.UserNotAuthorized:
        await Permissions.check_permissions(group, "get_group", check_permissions)

    members = (await actions.MembersActions.get_members(group)).members if include_members else None
    policies = (await actions.PolicyActions.get_policies(resource=group)).policies if include_policies else None
    workspace = WorkspaceSchemas.Workspace(**group.workspace.model_dump(exclude={"members",  # type: ignore
                                                                                 "policies",
                                                                                 "groups"}))
    # Return the workspace with the fetched resources
    return GroupSchemas.Group(id=group.id,
                              name=group.name,
                              description=group.description,
                              workspace=workspace,
                              members=members,
                              policies=policies)


# Update a group
async def update_group(group: Group,
                       group_data: GroupSchemas.GroupUpdateRequest,
                       check_permissions: bool = True) -> GroupSchemas.Group:
    try:
        await Permissions.check_permissions(group.workspace, "update_groups", check_permissions)
    except WorkspaceExceptions.UserNotAuthorized:
        await Permissions.check_permissions(group, "update_group", check_permissions)

    save_changes = False
    workspace: Workspace = group.workspace  # type: ignore
    # The group must belong to a workspace
    if not workspace:
        raise WorkspaceExceptions.WorkspaceNotFound(workspace)

    # Check if group name is provided
    if group_data.name and group_data.name != group.name:
        # Check if group name is unique
        for g in workspace.groups:
            if g.name == group_data.name:  # type: ignore
                raise GroupExceptions.NonUniqueName(group)
        group.name = group_data.name  # Update the group name
        save_changes = True
    # Check if group description is provided
    if group_data.description and group_data.description != group.description:
        group.description = group_data.description  # Update the group description
        save_changes = True

    # Save the updates
    if save_changes:
        await Group.save(group)
    # Return the updated group
    return GroupSchemas.Group(**group.model_dump())


# Delete a group
async def delete_group(group: Group,
                       check_permissions: bool = True):
    try:
        await Permissions.check_permissions(group.workspace, "delete_groups", check_permissions)
    except WorkspaceExceptions.UserNotAuthorized:
        await Permissions.check_permissions(group, "delete_group", check_permissions)

    workspace: Workspace = group.workspace  # type: ignore
    group_ref = DBRef(collection="Group", id=group.id)

    # Remove the group from group list in the workspace
    workspace.groups = [g for g in workspace.groups if g.id != group.id]  # type: ignore
    await Workspace.replace(workspace)

    # Delete the group
    await Group.delete(group)
    if await Group.get(group.id):
        raise GroupExceptions.ErrorWhileDeleting(group.id)

    # Delete group policy in the workspace and all policies stored in the group
    # MongoDB style: {"$or": [{"parent_resource": ref}, {"policy_holder": ref}]}
    # Beanie style: Or(Policy.parent_resource == ref, Policy.policy_holder == ref)
    await Policy.find(Or(Policy.parent_resource == group_ref,          # type: ignore
                         Policy.policy_holder == group_ref)).delete()  # type: ignore
