from enum import IntFlag

# from app.routes.group import router
# from app.schemas.user import UserID
# from app.schemas.group import GroupID


# Define the permissions
class Permissions(IntFlag):
    NONE = 0


GroupPermissions = IntFlag("GroupPermission", ['get_group_info',
                                              'delete_group',
                                              'update_group',
                                              'get_group_owner',
                                              'get_group_admins',
                                              'get_group_users',
                                              'get_group_members',
                                              'add_user_to_group',
                                              'get_member_details',
                                              'promote_user',
                                              'remove_member'])


# Check if a user has a permission
def check_permission(user_permission: IntFlag, required_permission: IntFlag) -> bool:
    """Check if a user has a right provided in the permission argument.
    If the user is not found or has no permission, the default permission NONE is used.
    In which case the function returns False, unless the required permission is also NONE.

    Args:
        :param user_permissions: Dictionary with keys as users and their permissions as the values.
        user (User): User to check the permission for.
        permission (Permissions): Required permissions.

    Returns:
        bool: True if the user has the required permission, False otherwise.
    """
    return user_permission & required_permission == required_permission


# Set the permission for a account
# def set_permission(user_list: dict, user_id: User, permission: Permissions) -> None:
#     user_list[user.id] = permission
