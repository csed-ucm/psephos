from unipoll_api import AccountManager
from unipoll_api.documents import Account, Workspace, Group, Policy, Resource, Member
from unipoll_api.schemas import MemberSchemas, PolicySchemas, GroupSchemas
from unipoll_api.exceptions import ResourceExceptions
from unipoll_api.utils import Permissions
from unipoll_api.utils.permissions import check_permissions
from unipoll_api.dependencies import get_member


# Helper function to get policies from a resource
# NOTE: This can be moved to utils
async def get_policies_from_resource(resource: Resource) -> list[Policy]:
    policies: list[Policy] = []
    try:
        await check_permissions(resource, "get_policies")
        return resource.policies  # type: ignore
    except ResourceExceptions.UserNotAuthorized:
        print("User not authorized")
        account = AccountManager.active_user.get()
        member = await get_member(account, resource)
        for policy in resource.policies:
            if policy.policy_holder.ref.id == member.id:  # type: ignore
                policies.append(policy)  # type: ignore
        return policies


# Get all policies of a workspace
async def get_policies(policy_holder: Member | Group | None = None,
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
    member, group = None, None
    if policy_holder.get_document_type() == "Member":
        await policy_holder.fetch_link("account")
        account: Account = policy_holder.account  # type: ignore
        member = MemberSchemas.Member(id=policy_holder.id,
                                      account_id=account.id,
                                      email=account.email,
                                      first_name=account.first_name,
                                      last_name=account.last_name)
    elif policy_holder.get_document_type() == "Group":
        group = GroupSchemas.Group(id=policy_holder.id,
                                   name=policy_holder.name,
                                   description=policy_holder.description)

    # Get the permissions based on the resource type and convert it to a list of strings
    permission_type = Permissions.PermissionTypes[parent_resource.get_document_type()]
    permissions = permission_type(policy.permissions).name.split('|')  # type: ignore

    # Return the policy
    return PolicySchemas.PolicyShort(id=policy.id,
                                     policy_holder_type=policy.policy_holder_type,
                                     policy_holder=member or group,
                                     permissions=permissions)


async def update_policy(policy: Policy,
                        new_permissions: list[str],
                        check_permissions: bool = True) -> PolicySchemas.PolicyOutput:

    parent_resource = await policy.get_parent_resource(fetch_links=True)

    # Check if the user has the required permissions to update the policy
    await Permissions.check_permissions(parent_resource, "update_policies", check_permissions)
    permission_type = Permissions.PermissionTypes[parent_resource.get_document_type()]

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
    member, group = None, None
    if policy_holder.get_document_type() == "Member":
        await policy_holder.fetch_link("account")
        account: Account = policy_holder.account  # type: ignore
        member = MemberSchemas.Member(id=policy_holder.id,
                                      account_id=account.id,
                                      email=account.email,
                                      first_name=account.first_name,
                                      last_name=account.last_name)
    elif policy_holder.get_document_type() == "Group":
        group = GroupSchemas.Group(id=policy_holder.id,
                                   name=policy_holder.name,
                                   description=policy_holder.description)

    return PolicySchemas.PolicyOutput(permissions=permission_type(policy.permissions).name.split('|'),  # type: ignore
                                      policy_holder=member or group)
