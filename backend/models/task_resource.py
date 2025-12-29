from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.database import Base


class TaskResource(Base):
    __tablename__ = "task_resources"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(500), nullable=False)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(100), nullable=True)  # e.g., "Khan Academy", "Wikipedia", etc.

    created_at = Column(DateTime(timezone=True), server_default=func.now())
