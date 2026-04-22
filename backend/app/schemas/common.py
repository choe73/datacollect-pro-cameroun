"""Common schemas."""

from typing import Generic, List, Optional, TypeVar, Dict, Any
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        """Calculate offset."""
        return (self.page - 1) * self.per_page


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: Optional[str] = None
    errors: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseModel):
    """Success response wrapper."""
    message: str
    data: Optional[Dict[str, Any]] = None


class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: float
    services: Dict[str, str]
