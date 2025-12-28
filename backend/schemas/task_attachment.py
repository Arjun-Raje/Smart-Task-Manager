from pydantic import BaseModel
from datetime import datetime


class TaskAttachmentResponse(BaseModel):
    id: int
    task_id: int
    filename: str
    content_type: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True
