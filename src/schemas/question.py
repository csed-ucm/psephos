from typing import Optional, Union
from pydantic import BaseModel
from src.documents import ResourceID


class Question(BaseModel):
    id: Optional[ResourceID]
    type: Optional[str]
    options: Optional[list[Union[str, bool, int, float]]]
    correct_answer: Optional[list[Union[str, bool, int, float]]]


class SingleChoiceQuestion(Question):
    type: str = "single-choice"


class MultipleChoiceQuestion(Question):
    type: str = "multiple-choice"


class OpenQuestion(Question):
    type: str = "open"
