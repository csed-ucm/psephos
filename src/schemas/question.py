from pydantic import BaseModel


class Question(BaseModel):
    id: int
    question: str
    question_type: str
    options: list[str]
    correct_answer: list[int]


class SingleChoiceQuestion(Question):
    question_type: str = "single-choice"


class MultipleChoiceQuestion(Question):
    question_type: str = "multiple-choice"


class OpenQuestion(Question):
    question_type: str = "open"


class QuestionList(BaseModel):
    questions: list[Question]
