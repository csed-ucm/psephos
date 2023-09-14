# APIRouter creates path operations for user module
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, Query, HTTPException

from src import dependencies as Dependencies
from src.documents import Poll
from src.account_manager import current_active_user
from src.exceptions.resource import APIException
from src.schemas import poll as PollSchemas
from src.schemas import workspace as WorkspaceSchema
from src.actions import poll as PollActions
from src.utils import permissions as Permissions

open_router = APIRouter()
router = APIRouter(dependencies=[Depends(Dependencies.check_poll_permission)])


query_params = list[Literal["all", "questions", "policies"]]


# Get poll by id
@router.get("/{poll_id}",
            response_description="Get a group",
            response_model=PollSchemas.Poll,
            response_model_exclude_defaults=True,
            response_model_exclude_none=True)
async def get_poll(poll: Poll = Depends(Dependencies.get_poll_model),
                   include: Annotated[query_params | None, Query()] = None) -> PollSchemas.Poll:
    try:
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
                    questions = (await PollActions.get_poll_questions(poll)).questions
            if "policies" in include:
                req_permissions = Permissions.PollPermissions["get_poll_policies"]  # type: ignore
                if Permissions.check_permission(permissions, req_permissions):
                    policies = (await PollActions.get_poll_policies(poll)).policies

        workspace = WorkspaceSchema.WorkspaceShort(**poll.workspace.dict())  # type: ignore

        # Return the workspace with the fetched resources
        return PollSchemas.Poll(id=poll.id,
                                name=poll.name,
                                description=poll.description,
                                public=poll.public,
                                published=poll.published,
                                workspace=workspace,
                                questions=questions,
                                policies=policies)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))