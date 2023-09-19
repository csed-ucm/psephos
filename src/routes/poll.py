# APIRouter creates path operations for user module
from typing import Annotated, Literal
from fastapi import APIRouter, Body, Depends, Query, HTTPException

from src import dependencies as Dependencies
from src.documents import Poll
from src.exceptions.resource import APIException
from src.schemas import poll as PollSchemas
from src.schemas import question as QuestionSchemas
from src.schemas import policy as PolicySchema
from src.actions import poll as PollActions

open_router = APIRouter()
router = APIRouter(dependencies=[Depends(Dependencies.check_poll_permission)])


query_params = list[Literal["all", "questions", "policies"]]


# Get poll by id
@router.get("/{poll_id}",
            response_description="Poll details",
            response_model=PollSchemas.PollResponse,
            response_model_exclude_none=True)
async def get_poll(poll: Poll = Depends(Dependencies.get_poll_model),
                   include: Annotated[query_params | None, Query()] = None):
    try:
        return await PollActions.get_poll(poll, list(include or []))
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Update poll details
@router.patch("/{poll_id}",
              response_description="Update Poll detail",
              response_model=PollSchemas.PollResponse,
              response_model_exclude_none=True)
async def update_poll(poll: Poll = Depends(Dependencies.get_poll_model),
                      data: PollSchemas.UpdatePollRequest = Body(...)):
    try:
        return await PollActions.update_poll(poll, data)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Delete poll by id
@router.delete("/{poll_id}",
               response_description="Result of delete operation",
               status_code=204)
async def delete_poll(poll: Poll = Depends(Dependencies.get_poll_model)):
    try:
        return await PollActions.delete_poll(poll)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Get list of questions in a poll
@router.get("/{poll_id}/questions",
            response_description="Questions in a poll",
            response_model=QuestionSchemas.QuestionList,
            response_model_exclude_none=True)
async def get_questions(poll: Poll = Depends(Dependencies.get_poll_model),
                        include: Annotated[query_params | None, Query()] = None):
    try:
        return await PollActions.get_poll_questions(poll)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


@router.get("/{poll_id}/policies",
            response_description="Policy list of a poll",
            response_model=PolicySchema.PolicyList,
            response_model_exclude_none=True)
async def get_policies(poll: Poll = Depends(Dependencies.get_poll_model),
                       include: Annotated[query_params | None, Query()] = None):
    try:
        return await PollActions.get_poll_policies(poll)
    except APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))
