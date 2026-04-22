"""Analysis endpoints."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.analysis import (
    DescriptiveRequest,
    DescriptiveAnalysisResponse,
    RegressionRequest,
    RegressionResult,
    PCARequest,
    PCAResult,
    ClassificationRequest,
    ClassificationResult,
    ClusteringRequest,
    ClusteringResult,
)
from app.services.analysis_service import AnalysisService

router = APIRouter()


@router.post("/descriptive", response_model=DescriptiveAnalysisResponse)
async def descriptive_analysis(
    request: DescriptiveRequest,
    db: AsyncSession = Depends(get_db),
):
    """Perform descriptive statistical analysis."""
    service = AnalysisService(db)
    try:
        result = await service.descriptive_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/regression", response_model=RegressionResult)
async def regression_analysis(
    request: RegressionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Perform regression analysis."""
    service = AnalysisService(db)
    try:
        result = await service.regression_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pca", response_model=PCAResult)
async def pca_analysis(
    request: PCARequest,
    db: AsyncSession = Depends(get_db),
):
    """Perform Principal Component Analysis."""
    service = AnalysisService(db)
    try:
        result = await service.pca_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/classification", response_model=ClassificationResult)
async def classification_analysis(
    request: ClassificationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Perform supervised classification."""
    service = AnalysisService(db)
    try:
        result = await service.classification_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/clustering", response_model=ClusteringResult)
async def clustering_analysis(
    request: ClusteringRequest,
    db: AsyncSession = Depends(get_db),
):
    """Perform unsupervised clustering."""
    service = AnalysisService(db)
    try:
        result = await service.clustering_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/results/{result_id}")
async def get_analysis_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a previous analysis result."""
    service = AnalysisService(db)
    result = await service.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result
