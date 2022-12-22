from fastapi.testclient import TestClient
from fastapi import status
import pytest
# from pydantic import BaseModel
# # from devtools import debug
from httpx import AsyncClient
# # from pydantic import BaseSettings
from app.app import app
# from beanie import PydanticObjectId
from app.utils import colored_dbg
from app.config import get_settings
import motor.motor_asyncio
from beanie import Document, Indexed, init_beanie
from app.models.user import User


pytestmark = pytest.mark.asyncio

# fake = Faker()
# client = TestClient(app)
settings = get_settings()

# TODO: Add settings for testing, i.e. testing database
# class Settings(BaseSettings):


async def test_database():
    colored_dbg.test_info("Testing database")
    colored_dbg.info(settings.mongodb_url)

    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url, uuidRepresentation="standard")
    colored_dbg.info(client)
    assert client is not None

    mainDB = client.app
    info = await mainDB.command("serverStatus")
    colored_dbg.info(info)

    await init_beanie(database=client.db_name, document_models=[User])
    colored_dbg.test_success("Database connection successful")


# async def get_user_db() -> AsyncGenerator:
    # yield BeanieUserDatabase(User)
