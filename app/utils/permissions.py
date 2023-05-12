from enum import IntFlag
import ast
from pathlib import Path
# from app.exceptions.resource import UserNotMember

# from app.models.documents import Policy

# Define the permissions base class as an IntFlag Enum
# The enumerator entries are combination of key: value (permission: #value) pairs,
# where value is an int powers of 2:
# permission1 = 1, 2^0, 0001
# permission2 = 2, 2^1, 0010
# permission3 = 4, 2^2, 0100
# permission4 = 8, 2^3, 1000
Permissions = IntFlag


# Parse action module (e.g. app/actions/workspace.py) to get the actions of the resource
# Create a permission class(IntFlag Enum) for that type of resource
# **param** resource_type: Name of the resource type (e.g. workspace, group)
def parse_action_file(resource_type: str) -> Permissions:
    parsed_ast = ast.parse(Path("app/actions/" + resource_type + ".py").read_text())
    actions = [node.name for node in ast.walk(parsed_ast) if isinstance(
        node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return Permissions(resource_type.capitalize() + "Permission", actions)


# Create permissions for each resource type
WorkspacePermissions = parse_action_file("workspace")
GroupPermissions = parse_action_file("group")


# Check if a user has a permission
def check_permission(user_permission, required_permission) -> bool:
    """Check if a user has a right provided in the permission argument.
    If the user is not found or has no permission, the default permission NONE is used.
    In which case the function returns False, unless the required permission is also NONE.

    Args:
        :param user_permissions: Dictionary with keys as users and their permissions as the values.
        :required_permission: Required permissions.

    Returns:
        bool: True if the user has the required permission, False otherwise.
    """
    return user_permission & required_permission == required_permission


async def get_all_permissions(resource, account):
    permission_sum = 0
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
                permission_sum |= policy.permissions
        # If there is a group that user is a member of, add group permissions to the user permissions
        elif policy.policy_holder_type == "group":
            group = await policy.policy_holder.fetch()
            await group.fetch_link("members")
            if account in group.members:
                permission_sum |= policy.permissions

    return permission_sum
