import os
import motor.motor_asyncio
from dotenv import load_dotenv
from fastapi_users.db import BeanieUserDatabase
from app.models.user import User

load_dotenv()

DATABASE_URL = os.environ["MONGODB_URL"]
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
Accounts_DB = client.accounts

async def get_user_db():
    yield BeanieUserDatabase(User)