from beanie import DeleteRules, WriteRules
from unipoll_api import AccountManager
from unipoll_api.documents import Policy, Workspace, Group, Account, create_link
from unipoll_api import actions
from unipoll_api.schemas import GroupSchemas, WorkspaceSchemas
from unipoll_api.exceptions import (GroupExceptions, WorkspaceExceptions)
from unipoll_api.utils import Permissions


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
        search_filter['members._id'] = account.id  # type: ignore
    search_result = await Group.find(search_filter, fetch_links=True).to_list()

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
                       description: str) -> GroupSchemas.GroupCreateOutput:
    # await workspace.fetch_link(workspace.groups)
    account = AccountManager.active_user.get()

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
    await new_group.add_member(account, Permissions.GROUP_ALL_PERMISSIONS)

    # Create a policy for the new group
    permissions = Permissions.WORKSPACE_BASIC_PERMISSIONS  # type: ignore
    new_policy = Policy(policy_holder_type='group',
                        policy_holder=(await create_link(new_group)),
                        permissions=permissions,
                        parent_resource=workspace)  # type: ignore

    # Add the group and the policy to the workspace
    workspace.policies.append(new_policy)  # type: ignore
    workspace.groups.append(new_group)  # type: ignore
    await Workspace.save(workspace, link_rule=WriteRules.WRITE)

    # Return the new group
    return GroupSchemas.GroupCreateOutput(**new_group.model_dump(include={'id', 'name', 'description'}))


# Get group
async def get_group(group: Group, include_members: bool = False, include_policies: bool = False) -> GroupSchemas.Group:
    account = AccountManager.active_user.get()

    # Check if the user has a permission to get all the groups in the workspace
    workspace_permissions = await Permissions.get_all_permissions(group.workspace, account)
    group_permissions = await Permissions.get_all_permissions(group, account)

    if not (Permissions.check_permission(workspace_permissions, Permissions.WorkspacePermissions["get_groups"]) or
            Permissions.check_permission(group_permissions, Permissions.GroupPermissions["get_group"])):
        raise GroupExceptions.UserNotAuthorized(
            account, group, f"to view group {group.id}")

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
                       group_data: GroupSchemas.GroupUpdateRequest) -> GroupSchemas.Group:
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
async def delete_group(group: Group):
    # await group.fetch_link(Group.workspace)
    workspace: Workspace = group.workspace  # type: ignore
    workspace.groups = [
        g for g in workspace.groups if g.id != group.id]  # type: ignore
    workspace.policies = [
        p for p in workspace.policies if p.policy_holder.ref.id != group.id]  # type: ignore
    await Workspace.save(workspace, link_rule=DeleteRules.DELETE_LINKS)
    await Group.delete(group)

    if await Group.get(group.id):
        return GroupExceptions.ErrorWhileDeleting(group.id)

    await Policy.find({"parent_resource._id": group.id}, fetch_links=True).delete()
