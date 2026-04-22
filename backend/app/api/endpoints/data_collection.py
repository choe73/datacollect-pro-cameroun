"""Data collection endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.celery_app import celery_app
from app.tasks.data_collection import (
    collect_world_bank_data,
    collect_nasa_power_data,
    collect_fao_data,
)

router = APIRouter()


@router.get("/sources")
async def list_sources():
    """List available data sources."""
    return {
        "sources": [
            {
                "id": "world_bank",
                "name": "World Bank Open Data",
                "url": "https://api.worldbank.org/v2",
                "status": "available",
                "last_update": None,
            },
            {
                "id": "nasa_power",
                "name": "NASA POWER (Météo)",
                "url": "https://power.larc.nasa.gov/api",
                "status": "available",
                "last_update": None,
            },
            {
                "id": "fao",
                "name": "FAO FAOSTAT",
                "url": "https://fenixservices.fao.org/faostat",
                "status": "available",
                "last_update": None,
            },
        ]
    }


@router.post("/trigger/{source_id}")
async def trigger_collection(
    source_id: str,
    background_tasks: BackgroundTasks,
    dry_run: bool = False,
):
    """Trigger data collection from a specific source."""
    
    task_mapping = {
        "world_bank": collect_world_bank_data,
        "nasa_power": collect_nasa_power_data,
        "fao": collect_fao_data,
    }
    
    if source_id not in task_mapping:
        raise HTTPException(status_code=400, detail=f"Unknown source: {source_id}")
    
    # Run task asynchronously
    task = task_mapping[source_id].delay(dry_run=dry_run)
    
    return {
        "message": f"Collection triggered for {source_id}",
        "task_id": task.id,
        "status": "pending",
    }


@router.post("/trigger/all")
async def trigger_all_collections(
    background_tasks: BackgroundTasks,
    dry_run: bool = False,
):
    """Trigger data collection from all sources."""
    
    tasks = []
    
    # Trigger all collections
    task_wb = collect_world_bank_data.delay(dry_run=dry_run)
    tasks.append({"source": "world_bank", "task_id": task_wb.id})
    
    task_nasa = collect_nasa_power_data.delay(dry_run=dry_run)
    tasks.append({"source": "nasa_power", "task_id": task_nasa.id})
    
    task_fao = collect_fao_data.delay(dry_run=dry_run)
    tasks.append({"source": "fao", "task_id": task_fao.id})
    
    return {
        "message": "All collections triggered",
        "tasks": tasks,
    }


@router.get("/status/{task_id}")
async def get_collection_status(task_id: str):
    """Get status of a collection task."""
    task = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None,
    }


@router.get("/history")
async def get_collection_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Get history of data collections."""
    # Query from CeleryJob model
    from sqlalchemy import select
    from app.models.celery_jobs import CeleryJob
    
    query = select(CeleryJob).order_by(CeleryJob.started_at.desc()).limit(limit)
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return {
        "history": [
            {
                "id": job.id,
                "task_name": job.task_name,
                "status": job.status,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
            }
            for job in jobs
        ]
    }
