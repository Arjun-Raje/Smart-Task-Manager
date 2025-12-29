from pydantic import BaseModel
from datetime import datetime


class TaskResourceResponse(BaseModel):
    id: int
    task_id: int
    title: str
    url: str
    description: str | None
    source: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResourceItem(BaseModel):
    title: str
    url: str
    description: str | None = None
    source: str | None = None
