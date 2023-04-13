from beanie import Document, Link
from app.models.user import User
from app.models.group import Group
# from app.models.workspace import Workspace
from app.utils.permissions import Permissions


class Policy(Document):
    """ 
    Policy model, based on Beanie Document class. This model is used to store information about permissions.
    Parameters:
    -----------
    member: Link[Group] | Link[User]
        The member of the group, either a user or another group.
    permissions: Permissions
        The permissions of the member.
    """

    policy_holder_type: str
    policy_holder: Link[Group] | Link[User]
    permissions: Permissions
