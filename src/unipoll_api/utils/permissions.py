from enum import IntFlag
import unipoll_api
from unipoll_api import exceptions

# import functools
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

WorkspacePermissions = IntFlag("WorkspacePermissions", ['get_workspace',
                                                        'update_workspace',
                                                        'delete_workspace',
                                                        'get_members',
                                                        'add_members',
                                                        'remove_members',
                                                        'get_groups',
                                                        'add_groups',
                                                        'update_groups',
                                                        'delete_groups',
                                                        'get_policies',
                                                        'add_policies',
                                                        'update_policies',
                                                        'delete_policies',
                                                        'get_polls',
                                                        'create_polls',
                                                        'delete_polls'])

GroupPermissions = IntFlag("GroupPermissions", ['get_group',
                                                'update_group',
                                                'delete_group',
                                                'get_members',
                                                'add_members',
                                                'remove_members',
                                                'get_policies',
                                                'add_policies',
                                                'update_policies',
                                                'delete_policies'])

PollPermissions = IntFlag("PollPermissions", ['get_poll',
                                              'get_questions',
                                              'update_poll',
                                              'delete_poll',
                                              'get_policies',
                                              'add_policies',
                                              'update_policies',
                                              'delete_policies'
                                              ])


PermissionTypes = {
    "Workspace": WorkspacePermissions,
    "Group": GroupPermissions,
    "Poll": PollPermissions
}


WORKSPACE_ALL_PERMISSIONS = WorkspacePermissions(-1)  # type: ignore
WORKSPACE_BASIC_PERMISSIONS = WorkspacePermissions(sum([WorkspacePermissions["get_workspace"],
                                                       WorkspacePermissions["get_members"],
                                                       WorkspacePermissions["get_polls"]]))  # type: ignore

GROUP_ALL_PERMISSIONS = GroupPermissions(-1)  # type: ignore
GROUP_BASIC_PERMISSIONS = (GroupPermissions["get_group"])  # type: ignore

POLL_ALL_PERMISSIONS = PollPermissions(-1)  # type: ignore
POLL_BASIC_PERMISSIONS = (PollPermissions["get_poll"])  # type: ignore


# Check if a user has a permission
def compare_permissions(user_permission: Permissions, required_permission: Permissions) -> bool:
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
async def get_all_permissions(resource, member) -> Permissions:
    permission_sum = 0
    # print("resource: ", resource.name)
    # await resource.fetch_link("policies")
    # print("policies: ", resource.policies)
    # Get policies for the resource
    for policy in resource.policies:
        # Get policy for the user
        if policy.policy_holder_type == "member":
            policy_holder_id = None
            if hasattr(policy.policy_holder, "id"):     # In case the policy_holder is an Account Document
                policy_holder_id = policy.policy_holder.id
            elif hasattr(policy.policy_holder, "ref"):  # In case the policy_holder is a Link
                policy_holder_id = policy.policy_holder.ref.id
            if policy_holder_id == member.id:
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
                if await get_all_permissions(group, member):
                    permission_sum |= policy.permissions
                    # print("Group permissions: ", policy.permissions)

    return permission_sum  # type: ignore


def convert_string_to_permission(resource_type: str, string: str):
    try:
        # return eval(get_document_type().capitalize() + "Permissions")[string]
        if resource_type == "Workspace":  # type: ignore
            req_permissions = WorkspacePermissions[string]  # type: ignore
        elif resource_type == "Group":  # type: ignore
            req_permissions = GroupPermissions[string]  # type: ignore
        elif resource_type == "Poll":  # type: ignore
            req_permissions = PollPermissions[string]  # type: ignore
        else:
            raise ValueError("Unknown resource type")
        return req_permissions
    except NameError:
        raise ValueError("Invalid permission string")


async def check_permissions(resource, required_permissions: str | list[str] | None = None, permission_check=True):
    if permission_check and required_permissions:
        account = unipoll_api.AccountManager.active_user.get()           # Get the active user

        from unipoll_api.dependencies import get_member
        member = await get_member(account, resource)

        user_permissions = await get_all_permissions(resource, member)  # Get the user permissions
        if isinstance(required_permissions, str):  # If only one permission is required
            required_permissions = [required_permissions]

        permissions_list = [convert_string_to_permission(resource.get_document_type(), p) for p in required_permissions]
        required_permission = eval(resource.get_document_type() + "Permissions")(sum(permissions_list))

        if not compare_permissions(user_permissions, required_permission):
            actions = ", ".join([" ".join([j.capitalize() for j in i.split("_")]) for i in required_permissions])
            raise exceptions.ResourceExceptions.UserNotAuthorized(account,
                                                                  f"{resource.get_document_type()} {resource.id}",
                                                                  actions)
