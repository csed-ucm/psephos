from unipoll_api.documents import Poll, Policy, Group, Account
from unipoll_api.schemas import poll as PollSchemas
from unipoll_api.schemas import question as QuestionSchemas
from unipoll_api.schemas import policy as PolicySchemas
from unipoll_api.schemas import member as MemberSchemas
from unipoll_api.schemas import workspace as WorkspaceSchema
from unipoll_api.utils import permissions as Permissions
from unipoll_api.exceptions import resource as GenericExceptions
from unipoll_api.account_manager import current_active_user


async def get_poll(poll: Poll, include: list[str]) -> PollSchemas.PollResponse:
    account = current_active_user.get()
    questions = []
    policies = None

    if include:
        # Get the permissions(allowed actions) of the current user
        permissions = await Permissions.get_all_permissions(poll, account)
        # If "all" is in the list, include all resources
        if "all" in include:
            include = ["policies", "questions"]
        # Fetch the resources if the user has the required permissions
        if "questions" in include:
            req_permissions = Permissions.PollPermissions["get_poll_questions"]  # type: ignore
            if Permissions.check_permission(permissions, req_permissions) or poll.public:
                questions = (await get_poll_questions(poll)).questions
        if "policies" in include:
            req_permissions = Permissions.PollPermissions["get_poll_policies"]  # type: ignore
            if Permissions.check_permission(permissions, req_permissions):
                policies = (await get_poll_policies(poll)).policies

    workspace = WorkspaceSchema.WorkspaceShort(**poll.workspace.dict())  # type: ignore

    # Return the workspace with the fetched resources
    return PollSchemas.PollResponse(id=poll.id,
                                    name=poll.name,
                                    description=poll.description,
                                    public=poll.public,
                                    published=poll.published,
                                    workspace=workspace,
                                    questions=questions,
                                    policies=policies)


async def get_poll_questions(poll: Poll) -> QuestionSchemas.QuestionList:
    print("Poll: ", poll.questions)
    question_list = []
    for question in poll.questions:
        # question_data = question.dict()
        question_scheme = QuestionSchemas.Question(**question)
        question_list.append(question_scheme)
    # Return the list of questions
    return QuestionSchemas.QuestionList(questions=question_list)


async def get_poll_policies(poll: Poll) -> PolicySchemas.PolicyList:
    policy_list = []
    policy: Policy
    for policy in poll.policies:  # type: ignore
        permissions = Permissions.pollPermissions(policy.permissions).name.split('|')  # type: ignore
        # Get the policy_holder
        if policy.policy_holder_type == 'account':
            policy_holder = await Account.get(policy.policy_holder.ref.id)
        elif policy.policy_holder_type == 'group':
            policy_holder = await Group.get(policy.policy_holder.ref.id)
        else:
            raise GenericExceptions.InternalServerError("Invalid policy_holder_type")
        if not policy_holder:
            # TODO: Replace with custom exception
            raise GenericExceptions.InternalServerError("get_poll_policies() => Policy holder not found")
        # Convert the policy_holder to a Member schema
        policy_holder = MemberSchemas.Member(**policy_holder.dict())  # type: ignore
        policy_list.append(PolicySchemas.PolicyShort(id=policy.id,
                                                     policy_holder_type=policy.policy_holder_type,
                                                     # Exclude unset fields(i.e. "description" for Account)
                                                     policy_holder=policy_holder.dict(exclude_unset=True),
                                                     permissions=permissions))
    return PolicySchemas.PolicyList(policies=policy_list)


async def update_poll(poll: Poll, data: PollSchemas.UpdatePollRequest) -> PollSchemas.PollResponse:
    # Update the poll
    if data.name:
        poll.name = data.name
    if data.description:
        poll.description = data.description
    if data.public is not None:
        poll.public = data.public
    if data.published is not None:
        poll.published = data.published
    if data.questions:
        poll.questions = data.questions

    # Save the updated poll
    await Poll.save(poll)
    return await get_poll(poll, [])


async def delete_poll(poll: Poll):
    # Delete the poll
    await Poll.delete(poll)

    # Check if the poll was deleted
    if await Poll.get(poll.id):
        raise GenericExceptions.InternalServerError("Poll not deleted")
