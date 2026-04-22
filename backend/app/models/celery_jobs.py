"""Celery jobs tracking model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


class CeleryJob(Base):
    """Celery task execution tracking."""

    __tablename__ = "celery_jobs"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(200), nullable=False, index=True)
    status = Column(
        String(20), default="pending"
    )  # pending, running, completed, failed
    params = Column(JSONB)
    result = Column(JSONB)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)

    def __repr__(self):
        return f"<CeleryJob(id={self.id}, task={self.task_name}, status={self.status})>"
