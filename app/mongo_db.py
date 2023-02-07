from beanie import Document, Link
from typing import AsyncGenerator
from bson import DBRef
import motor.motor_asyncio
from fastapi_users.db import BeanieUserDatabase
from app.models.user import User
from app.config import get_settings


settings = get_settings()

DATABASE_URL = settings.mongodb_url
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
mainDB = client.app


async def get_user_db() -> AsyncGenerator:
    yield BeanieUserDatabase(User)


# Create a link to the Document model
async def create_link(document: Document) -> Link:
    ref = DBRef(collection=document._document_settings.name,  # type: ignore
                id=document.id)
    link = Link(ref, User)
    return link
