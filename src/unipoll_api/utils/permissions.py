from enum import IntFlag
# import ast
# from pathlib import Path


# Define the permissions base class as an IntFlag Enum
# The enumerator entries are combination of key: value (permission: #value) pairs,
# where value is an int powers of 2:
# permission1 = 1, 2^0, 0001
# permission2 = 2, 2^1, 0010
# permission3 = 4, 2^2, 0100
# permission4 = 8, 2^3, 1000
Permissions = IntFlag


# Parse action module (e.g. src/actions/workspace.py) to get the actions of the resource
# Create a permission class(IntFlag Enum) for that type of resource
# **param** resource_type: Name of the resource type (e.g. workspace, group)
# def parse_action_file(resource_type: str) -> Permissions:
#     parsed_ast = ast.parse(Path("/actions/" + resource_type + ".py").read_text())
#     actions = [node.name for node in ast.walk(parsed_ast) if isinstance(
#         node, (ast.FunctionDef, ast.AsyncFunctionDef))]
#     return IntFlag(resource_type.capitalize() + "Permission", actions)


# # Create permissions for each resource type
# WorkspacePermissions = parse_action_file("workspace")
# GroupPermissions = parse_action_file("group")
# PollPermissions = parse_action_file("poll")

WorkspacePermissions = IntFlag("WorkspacePermissions", ['get_workspaces',
                                                        'create_workspace',
                                                        'get_workspace',
                                                        'update_workspace',
                                                        'delete_workspace',
                                                        'get_workspace_members',
                                                        'add_workspace_members',
                                                        'remove_workspace_member',
                                                        'get_groups',
                                                        'create_group',
                                                        'get_workspace_policies',
                                                        'get_workspace_policy',
                                                        'set_workspace_policy',
                                                        'get_polls',
                                                        'create_poll'])

GroupPermissions = IntFlag("GroupPermissions", ['get_group',
                                                'update_group',
                                                'delete_group',
                                                'get_group_members',
                                                'add_group_members',
                                                'remove_group_member',
                                                'get_group_policies',
                                                'get_group_policy',
                                                'set_group_policy'])

PollPermissions = IntFlag("PollPermissions", ['get_poll',
                                              'get_poll_questions',
                                              'get_poll_policies',
                                              'update_poll',
                                              'delete_poll'])

WORKSPACE_ALL_PERMISSIONS = WorkspacePermissions(-1)  # type: ignore
# WORKSPACE_BASIC_PERMISSIONS = (WorkspacePermissions["get_workspace"])  # type: ignore
WORKSPACE_BASIC_PERMISSIONS = WorkspacePermissions(WorkspacePermissions["get_workspace"] +  # type: ignore
                                                   WorkspacePermissions["get_workspace_members"] +  # type: ignore
                                                   WorkspacePermissions["get_workspace_policy"] +  # type: ignore
                                                   WorkspacePermissions["get_workspace_policies"] +  # type: ignore
                                                   WorkspacePermissions["get_groups"])  # type: ignore
# Example: (WorkspacePermissions["get_workspace"] + WorkspacePermissions["get_workspace_members"])

GROUP_ALL_PERMISSIONS = GroupPermissions(-1)  # type: ignore
GROUP_BASIC_PERMISSIONS = (GroupPermissions["get_group"])  # type: ignore

POLL_ALL_PERMISSIONS = PollPermissions(-1)  # type: ignore
# POLL_BASIC_PERMISSIONS = (PollPermissions["get_poll"])  # type: ignore


# Check if a user has a permission
def check_permission(user_permission: Permissions, required_permission: Permissions) -> bool:
    """Check if a user has a right provided in the permission argument.
    If the user is not found or has no permission, the default permission NONE is used.
    In which case the function returns False, unless the required permission is also NONE.

    Args:
        :param user_permissions: Dictionary with keys as users and their permissions as the values.
        :required_permission: Required permissions.

    Returns:
        bool: True if the user has the required permission, False otherwise.
    """
    return bool((user_permission & required_permission) == required_permission)


# TODO: Rename
async def get_all_permissions(resource, account) -> Permissions:
    permission_sum = 0
    # print("resource: ", resource.name)
    # await resource.fetch_link("policies")
    # print("policies: ", resource.policies)
    # Get policies for the resource
    for policy in resource.policies:
        # Get policy for the user
        if policy.policy_holder_type == "account":
            policy_holder_id = None
            if hasattr(policy.policy_holder, "id"):     # In case the policy_holder is an Account Document
                policy_holder_id = policy.policy_holder.id
            elif hasattr(policy.policy_holder, "ref"):  # In case the policy_holder is a Link
                policy_holder_id = policy.policy_holder.ref.id
            if policy_holder_id == account.id:
                # print("Found policy for user")
                permission_sum |= policy.permissions
                # print("User permissions: ", policy.permissions)
        # If there is a group that user is a member of, add group permissions to the user permissions
        elif policy.policy_holder_type == "group":
            # Try to fetch the group
            group = await policy.policy_holder.fetch()
            # BUG: sometimes links are not fetched properly
            # If fetching policy holder is not working, find the group manually
            if not group:
                from unipoll_api.documents import Group
                group = await Group.get(policy.policy_holder.ref.id)

            if group:
                await group.fetch_link("policies")
                # print("Checking group: ", group.name)
                if await get_all_permissions(group, account):
                    permission_sum |= policy.permissions
                    # print("Group permissions: ", policy.permissions)

    return permission_sum  # type: ignore
