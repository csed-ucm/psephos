from unipoll_api import AccountManager
from unipoll_api.documents import Account, Workspace, Group, Policy, Resource
from unipoll_api.schemas import MemberSchemas, PolicySchemas
from unipoll_api.exceptions import ResourceExceptions
from unipoll_api.utils import Permissions
from unipoll_api.utils.permissions import check_permissions


# Helper function to get policies from a resource
# NOTE: This can be moved to utils
async def get_policies_from_resource(resource: Resource) -> list[Policy]:
    policies: list[Policy] = []
    try:
        await check_permissions(resource, "get_policies")
        return resource.policies  # type: ignore
    except ResourceExceptions.UserNotAuthorized:
        account = AccountManager.active_user.get()
        for policy in resource.policies:
            if policy.policy_holder.ref.id == account.id:  # type: ignore
                policies.append(policy)  # type: ignore
        return policies


# Get all policies of a workspace
async def get_policies(policy_holder: Account | Group | None = None,
                       resource: Resource | None = None) -> PolicySchemas.PolicyList:
    policy_list = []
    policy: Policy
    all_policies = []

    # Get policies from a specific resource
    if resource:
        all_policies = await get_policies_from_resource(resource)
    # Get policies from all resources
    else:
        all_workspaces = Workspace.find(fetch_links=True)
        all_groups = Group.find(fetch_links=True)
        all_resources = await all_workspaces.to_list() + await all_groups.to_list()

        for resource in all_resources:
            all_policies += await get_policies_from_resource(resource)

    # Build policy list
    for policy in all_policies:
        # Filter by policy_holder if specified
        if policy_holder:
            if (policy.policy_holder.ref.id != policy_holder.id):
                continue
        policy_list.append(await get_policy(policy, False))
    # Return policy list
    return PolicySchemas.PolicyList(policies=policy_list)


async def get_policy(policy: Policy, permission_check: bool = True) -> PolicySchemas.PolicyShort:
    # Get the parent resource of the policy
    parent_resource = await policy.get_parent_resource(fetch_links=True)
    await check_permissions(parent_resource, "get_policies", permission_check)

    # Get the policy holder
    policy_holder = await policy.get_policy_holder()
    member = MemberSchemas.Member(**policy_holder.model_dump())

    # Get the permissions based on the resource type and convert it to a list of strings
    permission_type = Permissions.PermissionTypes[parent_resource.resource_type]
    permissions = permission_type(policy.permissions).name.split('|')  # type: ignore

    # Return the policy
    return PolicySchemas.PolicyShort(id=policy.id,
                                     policy_holder_type=policy.policy_holder_type,
                                     policy_holder=member.model_dump(exclude_unset=True),
                                     permissions=permissions)


async def update_policy(policy: Policy,
                        new_permissions: list[str],
                        check_permissions: bool = True) -> PolicySchemas.PolicyOutput:

    parent_resource = await policy.get_parent_resource(fetch_links=True)

    # Check if the user has the required permissions to update the policy
    await Permissions.check_permissions(parent_resource, "update_policies", check_permissions)
    permission_type = Permissions.PermissionTypes[parent_resource.resource_type]

    # Calculate the new permission value from request
    new_permission_value = 0
    for i in new_permissions:
        try:
            new_permission_value += permission_type[i].value
        except KeyError:
            raise ResourceExceptions.InvalidPermission(i)
    # Update permissions
    policy.permissions = permission_type(new_permission_value)
    await Policy.save(policy)

    policy_holder = await policy.get_policy_holder()

    return PolicySchemas.PolicyOutput(
        permissions=permission_type(policy.permissions).name.split('|'),  # type: ignore
        policy_holder=policy_holder.model_dump())
