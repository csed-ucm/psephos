# File to store all the custom exceptions

from beanie import PydanticObjectId
from app.models.user import User
from app.models.group import Group

# If user already exists in the group
def user_exists(email: str, group: Group):
    user = User.find_one({"email": email})
    if user.id in group.users:
        raise Exception("User already exists in group") 
