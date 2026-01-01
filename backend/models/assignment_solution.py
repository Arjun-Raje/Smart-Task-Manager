from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from db.database import Base


class AssignmentSolution(Base):
    __tablename__ = "assignment_solutions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)

    # The uploaded assignment file info
    assignment_filename = Column(String, nullable=False)
    assignment_stored_filename = Column(String, nullable=False)

    # AI-generated solutions
    questions = Column(JSON, nullable=False, default=list)  # List of identified questions
    solutions = Column(JSON, nullable=False, default=list)  # List of solution approaches

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
