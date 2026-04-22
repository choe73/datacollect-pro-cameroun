"""Health check endpoints."""

import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import redis_client
from app.schemas.common import HealthCheck

router = APIRouter()


@router.get("", response_model=HealthCheck)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check endpoint."""
    timestamp = time.time()
    services = {}

    # Check database
    try:
        await db.execute("SELECT 1")
        services["database"] = "healthy"
    except Exception as e:
        services["database"] = f"unhealthy: {str(e)}"

    # Check Redis
    try:
        await redis_client.ping()
        services["redis"] = "healthy"
    except Exception as e:
        services["redis"] = f"unhealthy: {str(e)}"

    # Determine overall status
    status = "healthy" if all(s == "healthy" for s in services.values()) else "degraded"

    return HealthCheck(
        status=status,
        version="1.0.0",
        timestamp=timestamp,
        services=services,
    )
