from unipoll_api.documents import ResourceID, Account, Group
from unipoll_api.exceptions import resource


# Exception for when a Group with the same name already exists
class NonUniqueName(resource.NonUniqueName):
    def __init__(self, group: Group):
        super().__init__("Group", resource_name=group.name)


# Exception for when an error occurs during Group creation
class ErrorWhileCreating(resource.ErrorWhileCreating):
    def __init__(self, group: Group):
        super().__init__("Group", resource_name=group.name)


# Exception for when a Group is not found
class GroupNotFound(resource.ResourceNotFound):
    def __init__(self, group_id: ResourceID):
        super().__init__("Group", resource_id=group_id)


# Not authorized
class UserNotAuthorized(resource.UserNotAuthorized):
    def __init__(self, account: Account, group: Group, action: str):
        super().__init__(account, f'group {group.name}', action)


# Exception for when a Group was not deleted successfully
class ErrorWhileDeleting(resource.ErrorWhileDeleting):
    def __init__(self, group_id: ResourceID):
        super().__init__("Workspace", resource_id=group_id)


# Exception for trying to add a member that already exists
class AddingExistingMember(resource.AddingExistingMember):
    def __init__(self, group: Group, user: Account):
        super().__init__(group, user)


# Action not found
class ActionNotFound(resource.ActionNotFound):
    def __init__(self, action: str):
        super().__init__('group', action)


# User is not a member of the group
class UserNotMember(resource.UserNotMember):
    def __init__(self, group: Group, user: Account):
        super().__init__(group, user)


# Error while removing a member
class ErrorWhileRemovingMember(resource.ErrorWhileRemovingMember):
    def __init__(self, group: Group, user: Account):
        super().__init__(group, user)
