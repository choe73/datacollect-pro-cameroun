"""Data collection tasks."""

import asyncio
from datetime import datetime
from typing import List, Dict, Any

from app.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.data_collector import (
    WorldBankCollector,
    NASAPowerCollector,
    FAOCollector,
)


@celery_app.task(bind=True, max_retries=3)
def collect_world_bank_data(self, dry_run: bool = False) -> Dict[str, Any]:
    """Collect data from World Bank API."""

    async def _collect():
        async with AsyncSessionLocal() as db:
            collector = WorldBankCollector(db)
            return await collector.collect_all_indicators(
                country_code="CMR",
                start_year=2000,
                end_year=2023,
            )

    try:
        if dry_run:
            return {
                "status": "dry_run",
                "source": "world_bank",
                "message": "Dry run - no data collected",
            }

        # Run async collection
        result = asyncio.run(_collect())
        result["task_id"] = self.request.id
        result["timestamp"] = datetime.utcnow().isoformat()
        return result

    except Exception as exc:
        # Retry with exponential backoff
        self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def collect_nasa_power_data(self, dry_run: bool = False) -> Dict[str, Any]:
    """Collect meteorological data from NASA POWER API."""

    async def _collect():
        async with AsyncSessionLocal() as db:
            collector = NASAPowerCollector(db)
            return await collector.collect_meteo_data(
                start_date="20200101",
                end_date="20231231",
            )

    try:
        if dry_run:
            return {
                "status": "dry_run",
                "source": "nasa_power",
                "message": "Dry run - no data collected",
            }

        result = asyncio.run(_collect())
        result["task_id"] = self.request.id
        result["timestamp"] = datetime.utcnow().isoformat()
        return result

    except Exception as exc:
        self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def collect_fao_data(self, dry_run: bool = False) -> Dict[str, Any]:
    """Collect agricultural data from FAO API."""

    async def _collect():
        async with AsyncSessionLocal() as db:
            collector = FAOCollector(db)
            return await collector.collect_agricultural_data(
                years=list(range(2010, 2024)),
            )

    try:
        if dry_run:
            return {
                "status": "dry_run",
                "source": "fao",
                "message": "Dry run - no data collected",
            }

        result = asyncio.run(_collect())
        result["task_id"] = self.request.id
        result["timestamp"] = datetime.utcnow().isoformat()
        return result

    except Exception as exc:
        self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@celery_app.task
def collect_all_sources(dry_run: bool = False) -> List[Dict[str, Any]]:
    """Collect data from all sources."""
    results = []

    tasks = [
        collect_world_bank_data,
        collect_nasa_power_data,
        collect_fao_data,
    ]

    for task in tasks:
        result = task.delay(dry_run=dry_run)
        results.append(
            {
                "task": task.name,
                "task_id": result.id,
                "status": "scheduled",
            }
        )

    return results
