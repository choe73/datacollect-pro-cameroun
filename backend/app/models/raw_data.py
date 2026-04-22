"""Raw data model for collected data."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


class RawData(Base):
    """Raw data collected from external sources."""

    __tablename__ = "raw_data"

    id = Column(BigInteger, primary_key=True, index=True)
    source = Column(String(100), nullable=False, index=True)
    dataset_name = Column(String(200))
    data = Column(JSONB, nullable=False)
    collected_at = Column(DateTime, default=datetime.utcnow, index=True)
    hash = Column(String(64), unique=True, index=True)
    status = Column(String(20), default="pending")  # pending, processed, error
    error_message = Column(Text)

    def __repr__(self):
        return f"<RawData(id={self.id}, source={self.source}, status={self.status})>"
