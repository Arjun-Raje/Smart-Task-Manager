from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class QuestionSolution(BaseModel):
    question_number: str
    question_text: str
    approach: str
    key_concepts: list[str]
    solution_steps: list[str]
    tips: str


class AssignmentSolutionResponse(BaseModel):
    id: int
    task_id: int
    assignment_filename: str
    questions: list[QuestionSolution]
    created_at: datetime

    class Config:
        from_attributes = True
