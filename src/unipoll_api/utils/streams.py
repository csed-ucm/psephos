import asyncio
from unipoll_api.documents import Resource
from . import colored_dbg as Debug


# async def update_generator(resource: Resource):
async def update_generator():
    i = 0
    try:
        while True:
            i += 1
            yield dict(data=i)
            await asyncio.sleep(0.2)
    except asyncio.CancelledError as e:
        Debug.info("Disconnected from client (via refresh/close)")
        raise e
