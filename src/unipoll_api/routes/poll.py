# APIRouter creates path operations for user module
from typing import Annotated, Literal
from fastapi import APIRouter, Body, Depends, Query, HTTPException

from unipoll_api import dependencies as Dependencies
from unipoll_api.documents import Poll
from unipoll_api.exceptions.resource import APIException
from unipoll_api.actions import PollActions
from unipoll_api.schemas import PollSchemas, QuestionSchemas, PolicySchemas
from unipoll_api import actions

open_router: APIRouter = APIRouter()
router: APIRouter = APIRouter()


query_params = list[Literal["all", "questions", "policies"]]


# Get poll by id
@router.get("/{poll_id}",
            response_description="Poll details",
            response_model=PollSchemas.PollResponse,
            response_model_exclude_none=True)
async def get_poll(poll: Poll = Depends(Dependencies.get_poll),
                   include: Annotated[query_params | None, Query()] = None):
    try:
        params = {}
        if include:
            if "all" in include:
                params = {"include_questions": True, "include_policies": True}
            else:
                if "questions" in include:
                    params = {"include_questions": True}
                if "policies" in include:
                    params = {"include_policies": True}
        return await PollActions.get_poll(poll, **params)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Update poll details
@router.patch("/{poll_id}",
              response_description="Update Poll detail",
              response_model=PollSchemas.PollResponse,
              response_model_exclude_none=True)
async def update_poll(poll: Poll = Depends(Dependencies.get_poll),
                      data: PollSchemas.UpdatePollRequest = Body(...)):
    try:
        return await PollActions.update_poll(poll, data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Delete poll by id
@router.delete("/{poll_id}",
               response_description="Result of delete operation",
               status_code=204)
async def delete_poll(poll: Poll = Depends(Dependencies.get_poll)):
    try:
        return await PollActions.delete_poll(poll)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get list of questions in a poll
@router.get("/{poll_id}/questions",
            response_description="Questions in a poll",
            response_model=QuestionSchemas.QuestionList,
            response_model_exclude_none=True)
async def get_questions(poll: Poll = Depends(Dependencies.get_poll),
                        include: Annotated[query_params | None, Query()] = None):
    try:
        return await PollActions.get_poll_questions(poll)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


@router.get("/{poll_id}/policies",
            response_description="Policy list of a poll",
            response_model=PolicySchemas.PolicyList,
            response_model_exclude_none=True)
async def get_policies(poll: Poll = Depends(Dependencies.get_poll),
                       include: Annotated[query_params | None, Query()] = None):
    try:
        return await actions.PolicyActions.get_policies(resource=poll)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))
