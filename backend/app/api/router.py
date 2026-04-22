"""Main API router."""

from fastapi import APIRouter

from app.api.endpoints import (
    datasets,
    analysis,
    data_collection,
    health,
)

# Main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
api_router.include_router(data_collection.router, prefix="/collect", tags=["Data Collection"])
