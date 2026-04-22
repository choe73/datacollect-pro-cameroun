"""Processed data model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProcessedData(Base):
    """Processed and structured data."""
    
    __tablename__ = "processed_data"
    
    id = Column(BigInteger, primary_key=True, index=True)
    raw_data_id = Column(BigInteger, ForeignKey("raw_data.id"))
    domain = Column(String(50), index=True)  # agriculture, sante, education...
    indicator = Column(String(100), index=True)
    region = Column(String(50), index=True)
    date_value = Column(DateTime, index=True)
    numeric_value = Column(Numeric(15, 5))
    string_value = Column(Text)
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    raw_data = relationship("RawData", back_populates="processed_data")
    
    def __repr__(self):
        return f"<ProcessedData(id={self.id}, domain={self.domain}, indicator={self.indicator})>"
