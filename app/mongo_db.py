from typing import AsyncGenerator
import motor.motor_asyncio
from fastapi_users.db import BeanieUserDatabase
from app.models import documents as Documents
from app.config import get_settings
from app.account_manager import AccessToken

settings = get_settings()

DATABASE_URL = settings.mongodb_url
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
mainDB = client.app


async def get_account_db() -> AsyncGenerator:
    yield BeanieUserDatabase(Documents.Account)  # type: ignore


DOCUMENT_MODELS = [
    AccessToken,
    Documents.Resource,
    Documents.Account,
    Documents.Group,
    Documents.Workspace,
    Documents.Policy
]
