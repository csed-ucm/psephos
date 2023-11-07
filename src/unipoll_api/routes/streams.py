from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from unipoll_api.utils.streams import update_generator


router = APIRouter()


@router.get("/updates",
            response=EventSourceResponse)
async def event_log():
    updates = update_generator()
    return EventSourceResponse(updates)
