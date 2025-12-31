from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .task import TaskResponse


class TaskShareCreate(BaseModel):
    email: str
    permission: str = "view"  # "view" or "edit"


class TaskShareResponse(BaseModel):
    id: int
    task_id: int
    shared_with_email: str
    permission: str
    shared_at: datetime

    class Config:
        from_attributes = True


class SharedTaskResponse(BaseModel):
    id: int
    title: str
    deadline: Optional[datetime] = None
    effort: Optional[str] = None
    completed: bool
    owner_email: str
    permission: str
    shared_at: datetime

    class Config:
        from_attributes = True
