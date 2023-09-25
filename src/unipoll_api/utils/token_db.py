from datetime import datetime, timezone
from typing import (
    Any,
    Dict,
    Generic,
    Optional,
    Type,
    TypeVar,
)

from beanie import Document, PydanticObjectId
from fastapi_users.authentication.strategy.db import AccessTokenDatabase
from pydantic import BaseModel, Field
from pymongo import IndexModel
from beanie.odm.enums import SortDirection


class BeanieBaseAccessToken(BaseModel):
    access_token: str
    refresh_token: str
    user_id: PydanticObjectId
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        indexes = [IndexModel("access_token", unique=True),
                   IndexModel("refresh_token", unique=True)]


class BeanieBaseAccessTokenDocument(BeanieBaseAccessToken, Document):  # type: ignore
    pass


AP_BEANIE = TypeVar("AP_BEANIE", bound=BeanieBaseAccessTokenDocument)


class BeanieAccessTokenDatabase(Generic[AP_BEANIE], AccessTokenDatabase[AP_BEANIE]):  # type: ignore
    """
    Access token database adapter for Beanie.

    :param access_token_model: Beanie access token model.
    """

    def __init__(self, access_token_model: Type[AP_BEANIE]):
        self.access_token_model = access_token_model

    async def get_by_token(self, token: str,
                           max_age: Optional[datetime] = None) -> Optional[AP_BEANIE]:
        query: Dict[str, Any] = {"access_token": token}
        if max_age is not None:
            query["created_at"] = {"$gte": max_age}
        res = await self.access_token_model.find_one(query)
        return res

    async def get_by_refresh_token(self, token: str) -> Optional[AP_BEANIE]:
        query: Dict[str, Any] = {"refresh_token": token}
        res = await self.access_token_model.find_one(query)
        return res

    # Returns find query (not a document)
    async def get_token_family_by_user_id(self, user_id: PydanticObjectId):
        access_token = self.access_token_model.find({"user_id": user_id},
                                                    sort=[("created_at", SortDirection.DESCENDING)])
        return access_token

    async def create(self, create_dict: Dict[str, Any]) -> AP_BEANIE:
        access_token = self.access_token_model(**create_dict)
        await access_token.create()
        return access_token

    async def update(
        self, access_token: AP_BEANIE, update_dict: Dict[str, Any]
    ) -> AP_BEANIE:
        for key, value in update_dict.items():
            setattr(access_token, key, value)
        await access_token.save()  # type: ignore
        return access_token

    async def delete(self, access_token: AP_BEANIE) -> None:
        await access_token.delete()  # type: ignore
