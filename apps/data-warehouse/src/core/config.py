# apps/data-warehouse/src/core/config.py
"""
Data Warehouse Service Configuration
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Data Warehouse service settings"""
    
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/vocelio")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    # Data Lake Configuration
    DATA_LAKE_STORAGE_PATH: str = os.getenv("DATA_LAKE_STORAGE_PATH", "./data_lake")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 1000000000))  # 1GB default
    
    # ETL Configuration
    ETL_BATCH_SIZE: int = int(os.getenv("ETL_BATCH_SIZE", 1000))
    ETL_PROCESSING_INTERVAL: int = int(os.getenv("ETL_PROCESSING_INTERVAL", 300))  # 5 minutes
    
    # Analytics Configuration
    ANALYTICS_RETENTION_DAYS: int = int(os.getenv("ANALYTICS_RETENTION_DAYS", 365))
    ENABLE_REAL_TIME_ANALYTICS: bool = os.getenv("ENABLE_REAL_TIME_ANALYTICS", "true").lower() == "true"
    
    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()
