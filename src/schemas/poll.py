from typing import Optional
from pydantic import BaseModel
from src.documents import ResourceID
from src.schemas.question import Question


class Poll(BaseModel):
    id: Optional[ResourceID]
    name: str
    description: str
    published: bool
    questions: list[Question]
    policies: Optional[list]

    class Config:
        schema_extra = {
            "example": {
                "id": "1a2b3c4d5e6f7g8h9i0j",
                "name": "Poll 01",
                "description": "This is an example poll",
                "published": True
            }
        }


class PollShort(BaseModel):
    id: ResourceID
    name: str
    description: str
    published: bool

    class Config:
        schema_extra = {
            "example": {
                "poll": {
                    "id": "1a2b3c4d5e6f7g8h9i0j",
                    "name": "Poll 01",
                    "description": "This is an example poll",
                    "published": True
                }
            }
        }


class PollList(BaseModel):
    polls: list[PollShort]

    class Config:
        schema_extra = {
            "example": {
                "polls": [
                    {
                        "id": "1a2b3c4d5e6f7g8h9i0j",
                        "name": "Poll 01",
                        "description": "This is an example poll",
                        "published": True
                    },
                    {
                        "id": "1a2b3c4d5e6f7g8h9i0j",
                        "name": "Poll 02",
                        "description": "This is an example poll",
                        "published": True
                    }
                ]
            }
        }