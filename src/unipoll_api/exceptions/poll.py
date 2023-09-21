from unipoll_api.exceptions import resource
from unipoll_api.documents import Poll, ResourceID, Account


# Exception for when a Poll with the same name already exists
class NonUniqueName(resource.NonUniqueName):
    def __init__(self, poll: Poll):
        super().__init__("Poll", resource_name=poll.name)


# Exception for when an error occurs during Poll creation
class ErrorWhileCreating(resource.ErrorWhileCreating):
    def __init__(self, poll: Poll):
        super().__init__("Poll", resource_name=poll.name)


# Exception for when a Poll is not found
class PollNotFound(resource.ResourceNotFound):
    def __init__(self, poll_id: ResourceID):
        super().__init__("Poll", resource_id=poll_id)


# Not authorized
class UserNotAuthorized(resource.UserNotAuthorized):
    def __init__(self, account: Account, poll: Poll, action: str):
        super().__init__(account, f'poll {poll.name}', action)


# Action not found
class ActionNotFound(resource.ActionNotFound):
    def __init__(self, action: str):
        super().__init__('poll', action)
