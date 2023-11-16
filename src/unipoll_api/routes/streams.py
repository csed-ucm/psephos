from fastapi import APIRouter, Depends, HTTPException
from fastapi import Body
from sse_starlette.sse import EventSourceResponse
from datetime import datetime
from unipoll_api.redis import listen_to_channel, publish_message
from unipoll_api.documents import Account, ResourceID, Workspace  # Event
from unipoll_api.utils.events import get_updates, get_event_stream
from unipoll_api.dependencies import get_current_active_user
from unipoll_api.exceptions import ResourceExceptions

router = APIRouter()


# For testing purposes only
# Endpoint to get all events for a resource
# Accepts a query parameter "since" to get all events after a certain time
@router.get("/updates/{resource_id}")
async def event_log(resource_id: ResourceID,
                    since: str = ""):
    try:
        if since == "":
            from unipoll_api.app import start_time
            time = start_time
        else:
            time = datetime.fromisoformat(since)
        return await get_updates(resource_id, time)
    except Exception as e:
        print(e)
        return HTTPException(status_code=404, detail="Resource not found")


# For testing purposes only
# Endpoint to log an event for a resource(workspace)
@router.post("/workspace/{workspace_id}/log")
async def generate_event(workspace_id: ResourceID,
                         event: dict = Body(...)):
    try:
        workspace = await Workspace.get(workspace_id)
        if not workspace:
            raise ResourceExceptions.ResourceNotFound("Workspace", workspace_id)
        new_event = await workspace.log_event(data={"message": event})
        return new_event
    except Exception as e:
        print(e)


# For testing purposes only
# Endpoint to get new events, that occur after this request
@router.get("/resource/{resource_id}/subscribe")
async def mongodb_subscribe(resource_id: ResourceID):
    try:
        return EventSourceResponse(get_event_stream(resource_id))
    except Exception as e:
        print(e)


# Endpoint to push notifications to a user
@router.post("/redis/push")
async def redis_push(user: Account = Depends(get_current_active_user),
                     message: dict = Body(...)):
    try:
        data = {
            "recipient_id": str(user.id),
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        await publish_message(data)
    except Exception as e:
        print(e)


# Endpoint to user notifications
@router.get("/redis/subscribe")
async def redis_subscribe(user: Account = Depends(get_current_active_user)):
    try:
        return EventSourceResponse(listen_to_channel(str(user.id)))
    except Exception as e:
        print(e)
