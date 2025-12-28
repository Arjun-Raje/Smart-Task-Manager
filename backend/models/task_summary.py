from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from db.database import Base


class TaskSummary(Base):
    __tablename__ = "task_summaries"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, unique=True)

    summary = Column(Text, nullable=False, default="")
    key_points = Column(JSON, nullable=False, default=list)
    concepts = Column(JSON, nullable=False, default=list)
    action_items = Column(JSON, nullable=False, default=list)
    study_tips = Column(JSON, nullable=False, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
