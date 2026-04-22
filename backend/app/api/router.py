"""Main API router."""

from fastapi import APIRouter

from app.api.endpoints import (
    datasets,
    analysis,
    data_collection,
    health,
    auth,
    subscriptions,
    analytics,
    consent,
    feedback,
)

# Main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
api_router.include_router(
    data_collection.router, prefix="/collect", tags=["Data Collection"]
)
api_router.include_router(
    subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"]
)
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(consent.router, prefix="/consent", tags=["Consent"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
