from unipoll_api.exceptions import resource
from unipoll_api.documents import ResourceID


# Exception for when a Policy is not found
class PolicyNotFound(resource.ResourceNotFound):
    def __init__(self, policy_id: ResourceID):
        super().__init__("Policy", resource_id=policy_id)
