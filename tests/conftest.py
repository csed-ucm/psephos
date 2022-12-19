"""Tests fixtures."""
import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from app.app import app
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# @pytest.fixture()
# def event_loop():
#     loop = asyncio.get_event_loop()

#     yield loop

#     pending = asyncio.tasks.all_tasks(loop)
#     loop.run_until_complete(asyncio.gather(*pending))
#     loop.run_until_complete(asyncio.sleep(1))

#     loop.close()


@pytest.fixture()
async def client_test():
    """
    Create an instance of the client.
    :return: yield HTTP client.
    """
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as ac:
            yield ac
