from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from db.database import Base


class TaskShare(Base):
    __tablename__ = "task_shares"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    shared_with_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission = Column(String, default="view")  # "view" or "edit"
    shared_at = Column(DateTime(timezone=True), server_default=func.now())

    # Unique constraint: can't share same task with same user twice
    __table_args__ = (UniqueConstraint('task_id', 'shared_with_id', name='unique_task_share'),)
