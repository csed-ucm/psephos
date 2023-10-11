from unipoll_api import AccountManager
from unipoll_api.documents import Account, Workspace, Group, Policy, Resource
from unipoll_api.schemas import MemberSchemas, PolicySchemas
from unipoll_api.exceptions import PolicyExceptions, ResourceExceptions
from unipoll_api.utils import Permissions


# Get all policies of a workspace
async def get_policies(policy_holder: Account | Group | None = None,
                       resource: Resource | None = None) -> PolicySchemas.PolicyList:
    policy_list = []
    policy: Policy

    account: Account = AccountManager.active_user.get()
    all_policies = []

    # Less efficient way of getting policies
    #
    # search_filter = {}
    # if policy_holder:
    #     search_filter['policy_holder.ref'] = policy_holder.ref
    # if resource:
    #     search_filter['parent_resource.ref'] = resource.ref
    # all_policies = await Policy.find(search_filter).to_list()
    # for policy in all_policies:
    #     permissions = await Permissions.get_all_permissions(policy.parent_resource, account)
    #     if policy.parent_resource.resource_type == "workspace":
    #         req_permissions = Permissions.WorkspacePermissions["get_workspace_policies"]
    #     elif policy.parent_resource.resource_type == "group":
    #         req_permissions = Permissions.GroupPermissions["get_group_policies"]
    #     elif policy.parent_resource.resource_type == "poll":
    #         req_permissions = Permissions.PollPermissions["get_poll_policies"]
    #     if Permissions.check_permission(permissions, req_permissions):
    #     elif policy_holder.id == policy.policy_holder.ref.id:
    #         policy_list.append(await get_policy(policy))
    #     policy_list.append(await get_policy(policy))

    # Helper function to get policies from a resource
    async def get_policies_from_resource(resource: Resource) -> list[Policy]:
        req_permissions: Permissions.Permissions | None = None
        if resource.resource_type == "workspace":
            req_permissions = Permissions.WorkspacePermissions["get_workspace_policies"]
        elif resource.resource_type == "group":
            req_permissions = Permissions.GroupPermissions["get_group_policies"]
        if req_permissions:
            permissions = await Permissions.get_all_permissions(resource, account)
            if Permissions.check_permission(permissions, req_permissions):
                return resource.policies  # type: ignore
        else:
            user_policy = await Policy.find_one({"policy_holder.ref": account.ref, "parent_resource.ref": resource.ref})
            return [user_policy] if user_policy else []
        return []

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
        policy_list.append(await get_policy(policy))
    # Return policy list
    return PolicySchemas.PolicyList(policies=policy_list)


async def get_policy(policy: Policy) -> PolicySchemas.PolicyShort:

    # NOTE: Alternatevely, we can check here if the user has the required permissions to get the policy

    # Convert policy_holder link to Member object
    ph_type = policy.policy_holder_type
    ph_ref = policy.policy_holder.ref.id
    policy_holder = await Account.get(ph_ref) if ph_type == "account" else await Group.get(ph_ref)

    if not policy_holder:
        raise PolicyExceptions.PolicyHolderNotFound(ph_ref)

    policy_holder = MemberSchemas.Member(**policy_holder.model_dump())  # type: ignore
    if policy.parent_resource.resource_type == "workspace":  # type: ignore
        PermissionType = Permissions.WorkspacePermissions
    elif policy.parent_resource.resource_type == "group":  # type: ignore
        PermissionType = Permissions.GroupPermissions
    elif policy.parent_resource.resource_type == "poll":  # type: ignore
        PermissionType = Permissions.PollPermissions
    else:
        raise ResourceExceptions.InternalServerError("Unknown resource type")

    permissions = PermissionType(policy.permissions).name.split('|')  # type: ignore
    return PolicySchemas.PolicyShort(id=policy.id,
                                     policy_holder_type=policy.policy_holder_type,
                                     policy_holder=policy_holder.model_dump(exclude_unset=True),
                                     permissions=permissions)


async def update_policy(policy: Policy, new_permissions: list[str]) -> PolicySchemas.PolicyOutput:

    # BUG: since the parent_resource is of multiple types, it is not fetched properly, so we fetch it manually
    await policy.parent_resource.fetch_all_links()  # type: ignore

    # Check if the user has the required permissions to update the policy
    account: Account = AccountManager.active_user.get()
    permissions = await Permissions.get_all_permissions(policy.parent_resource, account)
    if policy.parent_resource.resource_type == "workspace":  # type: ignore
        ResourcePermissions = Permissions.WorkspacePermissions
        req_permissions = Permissions.WorkspacePermissions["set_workspace_policy"]
    elif policy.parent_resource.resource_type == "group":  # type: ignore
        ResourcePermissions = Permissions.GroupPermissions
        req_permissions = Permissions.GroupPermissions["set_group_policy"]
    elif policy.parent_resource.resource_type == "poll":  # type: ignore
        ResourcePermissions = Permissions.PollPermissions
        req_permissions = Permissions.PollPermissions["set_poll_policy"]
    else:
        raise ResourceExceptions.InternalServerError("Unknown resource type")

    if not Permissions.check_permission(permissions, req_permissions):
        raise ResourceExceptions.UserNotAuthorized(account, "policy", "Update policy")

    # Calculate the new permission value from request
    new_permission_value = 0
    for i in new_permissions:
        try:
            new_permission_value += ResourcePermissions[i].value  # type: ignore
        except KeyError:
            raise ResourceExceptions.InvalidPermission(i)
    # Update permissions
    policy.permissions = ResourcePermissions(new_permission_value)  # type: ignore
    await Policy.save(policy)

    if policy.policy_holder_type == "account":
        policy_holder = await Account.get(policy.policy_holder.ref.id)
    elif policy.policy_holder_type == "group":
        policy_holder = await Group.get(policy.policy_holder.ref.id)

    return PolicySchemas.PolicyOutput(
        permissions=ResourcePermissions(policy.permissions).name.split('|'),  # type: ignore
        policy_holder=policy_holder.model_dump())  # type: ignore
