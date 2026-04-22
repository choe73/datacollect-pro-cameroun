"""Application configuration using Pydantic Settings."""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "datacollect"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        """Assemble database URL from components."""
        if isinstance(v, str):
            return v
        return (
            f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}"
            f"@{values.get('POSTGRES_HOST')}:{values.get('POSTGRES_PORT')}"
            f"/{values.get('POSTGRES_DB')}"
        )
    
    # Redis
    REDIS_URL: Optional[RedisDsn] = None
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    @validator("REDIS_URL", pre=True)
    def assemble_redis_url(cls, v: Optional[str], values: dict) -> str:
        """Assemble Redis URL."""
        if isinstance(v, str):
            return v
        return f"redis://{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/3"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/4"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # External APIs
    WORLD_BANK_API_URL: str = "https://api.worldbank.org/v2"
    OPEN_DATA_CAMEROON_URL: str = "https://cameroon.opendataforafrica.org/api"
    NASA_POWER_API_URL: str = "https://power.larc.nasa.gov/api/temporal/daily/point"
    FAO_API_URL: str = "https://fenixservices.fao.org/faostat/api/v1/en/data"
    
    # Render
    RENDER_EXTERNAL_URL: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True
        
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT == "development"


# Global settings instance
settings = Settings()
