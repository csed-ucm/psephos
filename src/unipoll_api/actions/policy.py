from unipoll_api import AccountManager
from unipoll_api.documents import Account, Workspace, Group, Policy, Resource
from unipoll_api.schemas import MemberSchemas, PolicySchemas
from unipoll_api.exceptions import PolicyExceptions
from unipoll_api.utils import Permissions


# Get all policies of a workspace
async def get_policies(policy_holder: Account | Group | None = None,
                       resource: Resource | None = None) -> PolicySchemas.PolicyList:
    policy_list = []
    policy: Policy

    account: Account = AccountManager.active_user.get()
    all_policies = []

    # Helper function to get policies from a resource
    async def get_policies_from_resource(resource: Resource) -> list[Policy]:
        req_permissions = None
        if resource.resource_type == "workspace":
            req_permissions = Permissions.WorkspacePermissions["get_workspace_policies"]
        elif resource.resource_type == "group":
            req_permissions = Permissions.GroupPermissions["get_group_policies"]
        if req_permissions:
            permissions = await Permissions.get_all_permissions(resource, account)
            if Permissions.check_permission(permissions, req_permissions):
                return resource.policies  # type: ignore
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

    # Convert policy_holder link to Member object
    ph_type = policy.policy_holder_type
    ph_ref = policy.policy_holder.ref.id
    policy_holder = await Account.get(ph_ref) if ph_type == "account" else await Group.get(ph_ref)

    if not policy_holder:
        raise PolicyExceptions.PolicyHolderNotFound(ph_ref)

    policy_holder = MemberSchemas.Member(**policy_holder.dict())
    permissions = Permissions.WorkspacePermissions(policy.permissions).name.split('|')  # type: ignore
    return PolicySchemas.PolicyShort(id=policy.id,
                                     policy_holder_type=policy.policy_holder_type,
                                     policy_holder=policy_holder.dict(exclude_unset=True),
                                     permissions=permissions)

    # if not account and account_id:
    #     raise AccountExceptions.AccountNotFound(account_id)

    # # Check if account is a member of the workspace
    # if account.id not in [member.id for member in workspace.members]:  # type: ignore
    #     raise WorkspaceExceptions.UserNotMember(workspace, account)

    # user_permissions = await Permissions.get_all_permissions(workspace, account)
    # return PolicySchemas.PolicyOutput(
    #     permissions=Permissions.WorkspacePermissions(user_permissions).name.split('|'),  # type: ignore
    #     policy_holder=MemberSchemas.Member(**account.dict()))
