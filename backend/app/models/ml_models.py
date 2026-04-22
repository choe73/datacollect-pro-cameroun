"""ML models storage."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


class MLModel(Base):
    """Trained machine learning models."""
    
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)  # regression, classification, clustering
    algorithm = Column(String(50), nullable=False)
    hyperparameters = Column(JSONB)
    metrics = Column(JSONB)  # R2, accuracy, silhouette...
    model_file_path = Column(String(500))
    training_data_query = Column(String)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<MLModel(id={self.id}, name={self.model_name}, type={self.model_type})>"
