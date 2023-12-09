from typing import Optional, Any
from pydantic import ConfigDict, BaseModel, model_validator
from unipoll_api.documents import ResourceID
from unipoll_api.schemas import question
from unipoll_api.schemas.question import Question
from unipoll_api.schemas.workspace import Workspace
from unipoll_api.schemas.policy import Policy


class PollResponse(BaseModel):
    id: ResourceID
    workspace: Any 
    name: str
    description: str
    public: bool
    published: bool
    questions: Optional[list[Question]] = None
    policies: Optional[list] = None
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "1a2b3c4d5e6f7g8h9i0j",
            "name": "Poll 01",
            "description": "This is an example poll",
            "published": True
        }
    })


class PollShort(BaseModel):
    id: ResourceID
    name: str
    description: str
    public: bool
    published: bool
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "poll": {
                "id": "1a2b3c4d5e6f7g8h9i0j",
                "name": "Poll 01",
                "description": "This is an example poll",
                "published": True
            }
        }
    })


class PollList(BaseModel):
    polls: list[PollShort]
    model_config = ConfigDict(json_schema_extra={
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
    })


class CreatePollRequest(BaseModel):
    name: str
    workspace: Optional[ResourceID] = None
    description: str
    public: bool
    published: bool
    questions: list[Question]
    
    @model_validator(mode='after')
    def validate_questions(self) -> 'CreatePollRequest':
        if len(self.questions) == 0 and self.published:
            raise ValueError('Poll must have at least one question')
        if self.questions:
            for question in self.questions:
                if question.id > len(self.questions):
                    raise ValueError('Question ID cannot be greater than the number of questions')
            if len(self.questions) != len(set([question.id for question in self.questions])):
                raise ValueError('Question IDs must be unique')
        return self


class UpdatePollRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    public: Optional[bool] = None
    published: Optional[bool] = None
    questions: Optional[list[Question]] = None
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Poll 01",
            "description": "This is an example poll",
            "published": True
        }
    })


# Forward references
from unipoll_api.schemas.workspace import Workspace, WorkspaceShort   # noqa: E402
Workspace.model_rebuild()
WorkspaceShort.model_rebuild()
