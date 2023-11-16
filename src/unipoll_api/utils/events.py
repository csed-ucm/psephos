import asyncio
from datetime import datetime
from unipoll_api.documents import ResourceID, Event, Resource
from unipoll_api.redis import publish_message
from . import colored_dbg as Debug


async def get_updates(resource_id: ResourceID, since: datetime):
    events = await Event.find(Event.resource_id == str(resource_id), Event.ts > since).to_list()
    return events


async def get_event_stream(resource_id: ResourceID):
    try:
        time = datetime.now()
        while True:
            events = await get_updates(resource_id, time)
            if events:
                time = events[-1].ts
                yield events
    except asyncio.CancelledError as e:
        Debug.info("Disconnected from client (via refresh/close)")
        raise e


async def notify_members(resource: Resource, message: dict):
    try:
        timestamp = datetime.now()
        for member in resource.members:
            # print(member)
            data = {"recipient_id": str(member.account.id),
                    "timestamp": str(timestamp),
                    "message": message}
            await publish_message(data)
    except Exception as e:
        print(e)
