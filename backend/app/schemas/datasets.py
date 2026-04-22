"""Dataset schemas."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DatasetBase(BaseModel):
    """Base dataset schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    source: str = Field(..., min_length=1, max_length=100)
    domain: str = Field(..., min_length=1, max_length=50)


class DatasetCreate(DatasetBase):
    """Schema for creating a dataset."""
    schema: Dict[str, str] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = None


class DatasetUpdate(BaseModel):
    """Schema for updating a dataset."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Dataset(DatasetBase):
    """Complete dataset schema."""
    id: int
    row_count: int = 0
    columns: List[str] = Field(default_factory=list)
    last_updated: datetime
    created_at: datetime
    schema: Dict[str, str] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class DatasetStats(BaseModel):
    """Dataset statistics."""
    dataset_id: int
    total_rows: int
    numeric_columns: List[str]
    categorical_columns: List[str]
    date_columns: List[str]
    null_counts: Dict[str, int]
    memory_usage_mb: float


class DatasetQuery(BaseModel):
    """Query parameters for dataset data."""
    columns: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
    limit: int = Field(100, ge=1, le=10000)
    offset: int = Field(0, ge=0)
