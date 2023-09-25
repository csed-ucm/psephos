import motor.motor_asyncio  # type: ignore
from unipoll_api import documents as Documents
from unipoll_api.config import get_settings

settings = get_settings()

DATABASE_URL = settings.mongodb_url
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
mainDB = client.app


DOCUMENT_MODELS = [
    Documents.AccessToken,
    Documents.Resource,
    Documents.Account,
    Documents.Group,
    Documents.Workspace,
    Documents.Policy,
    Documents.Poll,
]
