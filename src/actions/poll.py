from src.documents import Poll, Policy, Group, Account
from src.schemas import poll as PollSchemas
from src.schemas import question as QuestionSchemas
from src.schemas import policy as PolicySchemas
from src.schemas import member as MemberSchemas
from src.utils import permissions as Permissions
from src.exceptions import resource as GenericExceptions


def get_poll(poll: Poll) -> PollSchemas.Poll:
    return PollSchemas.Poll(**poll.dict())


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
