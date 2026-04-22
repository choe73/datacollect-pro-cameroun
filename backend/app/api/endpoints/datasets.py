"""Dataset endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.schemas.datasets import Dataset, DatasetStats, DatasetQuery, PaginatedResponse
from app.services.dataset_service import DatasetService

router = APIRouter()


@router.get("", response_model=List[Dataset])
async def list_datasets(
    domain: Optional[str] = None,
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all datasets with optional filtering."""
    service = DatasetService(db)
    datasets = await service.list_datasets(domain=domain, source=source)
    return datasets


@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific dataset by ID."""
    service = DatasetService(db)
    dataset = await service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.get("/{dataset_id}/stats", response_model=DatasetStats)
async def get_dataset_stats(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get statistics for a dataset."""
    service = DatasetService(db)
    stats = await service.get_statistics(dataset_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return stats


@router.post("/{dataset_id}/query")
async def query_dataset(
    dataset_id: int,
    query: DatasetQuery,
    db: AsyncSession = Depends(get_db),
):
    """Query dataset with filters and pagination."""
    service = DatasetService(db)
    result = await service.query_data(dataset_id, query)
    return result


@router.get("/{dataset_id}/data")
async def get_dataset_data(
    dataset_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=1000),
    columns: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get raw data from a dataset."""
    service = DatasetService(db)
    column_list = columns.split(",") if columns else None
    data = await service.get_data(
        dataset_id, 
        page=page, 
        per_page=per_page,
        columns=column_list
    )
    return data
