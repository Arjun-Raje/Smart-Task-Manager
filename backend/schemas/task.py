from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    deadline: Optional[datetime] = None
    effort: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    deadline: Optional[datetime] = None
    effort: Optional[str] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    deadline: Optional[datetime] = None
    effort: Optional[str] = None
    completed: bool

    class Config:
        from_attributes = True
