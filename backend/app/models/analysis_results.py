"""Analysis results model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class AnalysisResult(Base):
    """Results of statistical analyses."""
    
    __tablename__ = "analysis_results"
    
    id = Column(BigInteger, primary_key=True, index=True)
    analysis_type = Column(String(50), nullable=False)  # descriptive, regression, pca, classification
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    input_params = Column(JSONB)
    results = Column(JSONB)
    visualizations = Column(JSONB)  # URLs or plot data
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    model = relationship("MLModel")
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, type={self.analysis_type})>"
