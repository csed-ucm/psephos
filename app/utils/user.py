from beanie.operators import In
from app.models.group import Group
from app.models.user  import User


# Desc
async def get_user_groups(user: User):
    """Get all groups that a user is a member of. 
    The function returns a list of dictionaries with role as a key and and a list of groups as a value.

    Args:
        user (User): User object with list of group ids

    Returns:
        Dict(str, List[Group]): Dictionary with groups separated by role
    """
    groups = await Group.find(In(Group.id, user.groups)).to_list()
    result = []
    for group in groups:
        if user.id == group.owner:
            result.append({"group_name": group.name, "role": "owner"})
        elif user.id in group.admins:
            result.append({"group_name": group.name, "role": "admin"})
        elif user.id in group.members:
            result.append({"group_name": group.name, "role": "user"})

        # groups = await Group.find({"$or": [{"owner": user_id}, {"members": user.id}, {"admins": user.id}]}).to_list()
    return result