from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # App
    app_name: str = "Compliance Service"
    debug: bool = False
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/vocelio")
    
    # Compliance APIs
    telecom_api_key: str = os.getenv("TELECOM_API_KEY", "")
    gdpr_compliance_endpoint: str = os.getenv("GDPR_ENDPOINT", "")
    
    # Audit settings
    audit_retention_days: int = 2555  # 7 years
    recording_retention_days: int = 1095  # 3 years
    
    # Regulatory bodies
    fcc_api_key: str = os.getenv("FCC_API_KEY", "")
    crtc_api_key: str = os.getenv("CRTC_API_KEY", "")
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
