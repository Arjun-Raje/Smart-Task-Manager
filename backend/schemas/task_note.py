from pydantic import BaseModel
from datetime import datetime


class TaskNoteUpdate(BaseModel):
    content: str


class TaskNoteResponse(BaseModel):
    id: int
    task_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
