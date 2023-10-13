from beanie import WriteRules
from unipoll_api.documents import Poll, Workspace
from unipoll_api.schemas import PollSchemas, QuestionSchemas, WorkspaceSchemas
from unipoll_api.utils import Permissions
from unipoll_api.exceptions import ResourceExceptions, PollExceptions
from unipoll_api import actions


async def get_polls(workspace: Workspace | None = None,
                    check_permissions: bool = True) -> PollSchemas.PollList:
    all_workspaces = [workspace] if workspace else await Workspace.find(fetch_links=True).to_list()

    poll_list = []
    for workspace in all_workspaces:
        try:
            await Permissions.check_permissions(workspace, "get_polls", check_permissions)
            poll_list += workspace.polls  # type: ignore
        except ResourceExceptions.UserNotAuthorized:
            poll: Poll
            for poll in workspace.polls:  # type: ignore
                if poll.public:
                    poll_list.append(poll)
                else:
                    poll_list.append(await get_poll(poll, check_permissions))  # type: ignore
    # Build poll list and return the result
    for poll in poll_list:  # type: ignore
        poll_list.append(PollSchemas.PollShort(**poll.model_dump()))  # type: ignore
    return PollSchemas.PollList(polls=poll_list)


# Create a new poll in a workspace
async def create_poll(workspace: Workspace,
                      input_data: PollSchemas.CreatePollRequest,
                      check_permissions: bool = True) -> PollSchemas.PollResponse:
    # Check if the user has permission to create polls
    await Permissions.check_permissions(actions, "create_polls", check_permissions)

    # Check if poll name is unique
    poll: Poll  # For type hinting, until Link type is supported
    for poll in workspace.polls:  # type: ignore
        if poll.name == input_data.name:
            raise PollExceptions.NonUniqueName(poll)

    # Create a new poll
    new_poll = Poll(name=input_data.name,
                    description=input_data.description,
                    workspace=workspace,  # type: ignore
                    public=input_data.public,
                    published=input_data.published,
                    questions=input_data.questions,
                    policies=[])

    # Check if poll was created
    if not new_poll:
        raise PollExceptions.ErrorWhileCreating(new_poll)

    # Add the poll to the workspace
    workspace.polls.append(new_poll)  # type: ignore
    await Workspace.save(workspace, link_rule=WriteRules.WRITE)

    # Return the new poll
    return PollSchemas.PollResponse(**new_poll.model_dump())


async def get_poll(poll: Poll,
                   include_questions: bool = False,
                   include_policies: bool = False,
                   check_permissions: bool = True) -> PollSchemas.PollResponse:
    if not poll.public:
        await Permissions.check_permissions(poll, "get_poll", check_permissions)

    # Fetch the resources if the user has the required permissions
    questions = (await get_poll_questions(poll)).questions if include_questions else None
    policies = (await actions.PolicyActions.get_policies(resource=poll)).policies if include_policies else None

    workspace = WorkspaceSchemas.WorkspaceShort(**poll.workspace.model_dump())  # type: ignore

    # Return the workspace with the fetched resources
    return PollSchemas.PollResponse(id=poll.id,
                                    name=poll.name,
                                    description=poll.description,
                                    public=poll.public,
                                    published=poll.published,
                                    workspace=workspace,
                                    questions=questions,
                                    policies=policies)


async def get_poll_questions(poll: Poll,
                             check_permissions: bool = True) -> QuestionSchemas.QuestionList:
    # Check if the user has permission to get questions
    if not poll.public:
        await Permissions.check_permissions(poll, "get_questions", check_permissions)

    question_list = []
    for question in poll.questions:
        # question_data = question.model_dump()
        question_scheme = QuestionSchemas.Question(**question)
        question_list.append(question_scheme)
    # Return the list of questions
    return QuestionSchemas.QuestionList(questions=question_list)


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
    return await get_poll(poll, include_questions=True)


async def delete_poll(poll: Poll):
    # Delete the poll
    await Poll.delete(poll)

    # Check if the poll was deleted
    if await Poll.get(poll.id):
        raise ResourceExceptions.InternalServerError("Poll not deleted")
