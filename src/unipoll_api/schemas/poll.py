from typing import Optional, Any
from pydantic import BaseModel
from unipoll_api.documents import ResourceID
from unipoll_api.schemas.question import Question


class PollResponse(BaseModel):
    id: Optional[ResourceID]
    # workspace: Optional[Union['Workspace', 'WorkspaceShort']]
    workspace: Optional[Any]
    name: str
    description: str
    public: bool
    published: bool
    questions: Optional[list[Question]]
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
    public: bool
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


class CreatePollRequest(BaseModel):
    name: str
    description: str
    public: bool
    published: bool
    questions: list[Question]


class UpdatePollRequest(BaseModel):
    name: Optional[str]
    description: Optional[str]
    public: Optional[bool]
    published: Optional[bool]
    questions: Optional[list[Question]]

    class Config:
        schema_extra = {
            "example": {
                "name": "Poll 01",
                "description": "This is an example poll",
                "published": True
            }
        }


# Forward references
from unipoll_api.schemas.workspace import Workspace, WorkspaceShort   # noqa: E402
Workspace.update_forward_refs()
WorkspaceShort.update_forward_refs()
