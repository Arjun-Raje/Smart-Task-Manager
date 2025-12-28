from pydantic import BaseModel
from datetime import datetime


class TaskSummaryResponse(BaseModel):
    id: int
    task_id: int
    summary: str
    key_points: list[str]
    concepts: list[str]
    action_items: list[str]
    study_tips: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
