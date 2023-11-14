import asyncio
from datetime import datetime
from unipoll_api.documents import Resource, Event
from . import colored_dbg as Debug


async def get_updates(resource: Resource, since: datetime):
    events = await Event.find(Event.resource_id == str(resource.id), Event.ts > since).to_list()
    return events


async def timeseries_generator(resource: Resource):
    try:
        time = datetime.now()
        while True:
            events = await get_updates(resource, time)
            if events:
                time = events[-1].ts
                yield events
    except asyncio.CancelledError as e:
        Debug.info("Disconnected from client (via refresh/close)")
        raise e


async def event_generator(resource: Resource):
    try:
        while True:
            print(resource.events)
            await asyncio.sleep(1)
            if resource.events:
                print("Event found")
                event = resource.events.pop()
                print(event)
                yield True
    except asyncio.CancelledError as e:
        Debug.info("Disconnected from client (via refresh/close)")
        raise e
