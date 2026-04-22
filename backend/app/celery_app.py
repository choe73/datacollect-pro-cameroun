"""Celery application configuration."""

from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "datacollect",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.data_collection",
        "app.tasks.data_processing",
        "app.tasks.ml_training",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Douala",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3000,  # 50 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=86400,  # 24 hours
)

# Beat schedule
celery_app.conf.beat_schedule = {
    "collect-world-bank-daily": {
        "task": "app.tasks.data_collection.collect_world_bank_data",
        "schedule": 86400.0,  # Daily
    },
    "collect-meteo-daily": {
        "task": "app.tasks.data_collection.collect_nasa_power_data",
        "schedule": 86400.0,
    },
    "clean-old-data": {
        "task": "app.tasks.data_processing.clean_old_raw_data",
        "schedule": 604800.0,  # Weekly
    },
}
