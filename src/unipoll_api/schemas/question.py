from typing import Any, Literal
from pydantic import BaseModel, ValidationInfo, field_validator, model_validator


question_types = Literal['single-choice', 'multiple-choice']


class Question(BaseModel):
    id: int
    question: str
    question_type: question_types
    options: list[str]
    correct_answer: list[int]
    
    @field_validator('id')
    @classmethod
    def id_positive(cls, v: int):
        if v <= 0:
            raise ValueError('ID cannot be negative or zero')
        return v

    @field_validator('correct_answer')
    @classmethod
    def correct_answer_positive(cls, v: list[int]):
        for i in v:
            if i < 0:
                raise ValueError('Correct answer cannot be negative')
        return v
    
    @field_validator('correct_answer')
    @classmethod
    def correct_answer_unique(cls, v: list[int]):
        if len(v) != len(set(v)):
            raise ValueError('Correct answer must be unique')
        return v

    @model_validator(mode='after')
    # @classmethod
    def validate_correct_answer(self) -> 'Question':
        if len(self.correct_answer) > 1 and self.question_type == 'single-choice':
            raise ValueError('Single choice question cannot have multiple correct answers')
        # if len(v) == 0 and values['question_type'] != 'open':
        #     raise ValueError('Question must have at least one correct answer')
        if len(self.correct_answer) > len(self.options):
            raise ValueError('Number of Correct options cannot be greater than the number of options')
        for i in self.correct_answer:
            if i >= len(self.options):
                raise ValueError('Correct answer cannot be greater than the number of options')
        
        return self


class SingleChoiceQuestion(Question):
    question_type: str = "single-choice"


class MultipleChoiceQuestion(Question):
    question_type: str = "multiple-choice"


class OpenQuestion(Question):
    question_type: str = "open"


class QuestionList(BaseModel):
    questions: list[Question]
