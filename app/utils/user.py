from beanie.operators import In
from app.models.group import Group
from app.models.user import User
from pydantic import EmailStr
from app.schemas.user import UserID
from app.schemas.group import GroupReadSimple, GroupList
from app.exceptions.user import UserNotFound


# Get all groups that a user is a member of with the user's role in that group
async def get_user_groups(user: User) -> GroupList:
    """Get all groups that a user is a member of.
    The function returns a list of dictionaries with role as a key and and a list of groups as a value.

    Args:
        user (User): User object with list of group ids

    Returns:
        GroupList: Model with the list of groups that user belongs to and the user's role in that group.
    """
    groups = await Group.find(In(Group.id, user.groups)).to_list()
    result = []
    for group in groups:
        if user.id == group.owner:
            result.append(GroupReadSimple(name=group.name, role="owner"))
        elif user.id in group.admins:
            result.append(GroupReadSimple(name=group.name, role="admin"))
        elif user.id in group.members:
            result.append(GroupReadSimple(name=group.name, role="user"))

    group_list = GroupList(groups=result)
    return group_list


# Check if user exists in the database
async def check_user_exists(user: User | UserID | EmailStr) -> User:
    """Check if user exists in the database

    Args:
        user (User): User object

    Returns:
        User: returns User object of found user, raises a HTTP exception otherwise
    """
    if isinstance(user, User):
        found_user = await User.get(user.id)
    elif isinstance(user, UserID):
        found_user = await User.get(user)
    elif isinstance(user, EmailStr):
        found_user = await User.find_one({"email": user})
    else:
        # Display error message with the type of the user object
        raise TypeError("Invalid type for user", type(user))

    if not found_user:
        raise UserNotFound(str(user))
    return found_user
