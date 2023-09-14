from src.exceptions import resource
from src.documents import Poll


# Exception for when a Poll with the same name already exists
class NonUniqueName(resource.NonUniqueName):
    def __init__(self, poll: Poll):
        super().__init__("Group", resource_name=poll.name)


# Exception for when an error occurs during Poll creation
class ErrorWhileCreating(resource.ErrorWhileCreating):
    def __init__(self, poll: Poll):
        super().__init__("Group", resource_name=poll.name)
