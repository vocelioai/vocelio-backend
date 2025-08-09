"""
AI Brain Service Configuration
Environment-specific settings and configuration management
"""

from pydantic import BaseSettings, Field
from typing import List, Optional, Dict, Any
import os

class AIBrainSettings(BaseSettings):
    """AI Brain service configuration"""
    
    # Service basic info
    service_name: str = Field(default="ai-brain", env="SERVICE_NAME")
    service_version: str = Field(default="1.0.0", env="SERVICE_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    port: int = Field(default=8007, env="PORT")
    
    # Database configuration
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # OpenAI configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    openai_timeout: int = Field(default=30, env="OPENAI_TIMEOUT")
    
    # AI model configuration
    max_conversation_history: int = Field(default=50, env="MAX_CONVERSATION_HISTORY")
    confidence_threshold: float = Field(default=0.8, env="CONFIDENCE_THRESHOLD")
    optimization_threshold: float = Field(default=0.85, env="OPTIMIZATION_THRESHOLD")
    
    # Real-time processing
    real_time_optimization: bool = Field(default=True, env="REAL_TIME_OPTIMIZATION")
    optimization_interval_seconds: int = Field(default=30, env="OPTIMIZATION_INTERVAL")
    batch_processing_enabled: bool = Field(default=True, env="BATCH_PROCESSING_ENABLED")
    max_concurrent_optimizations: int = Field(default=10, env="MAX_CONCURRENT_OPTIMIZATIONS")
    
    # Machine Learning configuration
    ml_model_update_frequency: str = Field(default="daily", env="ML_MODEL_UPDATE_FREQUENCY")
    auto_retrain_enabled: bool = Field(default=True, env="AUTO_RETRAIN_ENABLED")
    model_performance_threshold: float = Field(default=0.9, env="MODEL_PERFORMANCE_THRESHOLD")
    
    # Analytics and monitoring
    analytics_enabled: bool = Field(default=True, env="ANALYTICS_ENABLED")
    metrics_collection_interval: int = Field(default=60, env="METRICS_COLLECTION_INTERVAL")
    performance_monitoring: bool = Field(default=True, env="PERFORMANCE_MONITORING")
    
    # Security settings
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    requests_per_minute: int = Field(default=100, env="REQUESTS_PER_MINUTE")
    burst_limit: int = Field(default=200, env="BURST_LIMIT")
    
    # External service URLs
    api_gateway_url: str = Field(..., env="API_GATEWAY_URL")
    voice_lab_url: str = Field(..., env="VOICE_LAB_URL")
    call_center_url: str = Field(..., env="CALL_CENTER_URL")
    analytics_pro_url: str = Field(..., env="ANALYTICS_PRO_URL")
    
    # Redis configuration (for caching and real-time features)
    redis_url: str = Field(..., env="REDIS_URL")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    
    # Logging configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    structured_logging: bool = Field(default=True, env="STRUCTURED_LOGGING")
    log_to_file: bool = Field(default=False, env="LOG_TO_FILE")
    log_file_path: str = Field(default="/var/log/ai-brain.log", env="LOG_FILE_PATH")
    
    # Error handling
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay_seconds: int = Field(default=1, env="RETRY_DELAY_SECONDS")
    circuit_breaker_enabled: bool = Field(default=True, env="CIRCUIT_BREAKER_ENABLED")
    
    # Feature flags
    experimental_features_enabled: bool = Field(default=False, env="EXPERIMENTAL_FEATURES")
    advanced_analytics: bool = Field(default=True, env="ADVANCED_ANALYTICS")
    real_time_insights: bool = Field(default=True, env="REAL_TIME_INSIGHTS")
    auto_optimization: bool = Field(default=True, env="AUTO_OPTIMIZATION")
    
    # Performance tuning
    worker_processes: int = Field(default=4, env="WORKER_PROCESSES")
    max_request_size: int = Field(default=10485760, env="MAX_REQUEST_SIZE")  # 10MB
    request_timeout: int = Field(default=300, env="REQUEST_TIMEOUT")  # 5 minutes
    
    # Development settings
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    reload_on_change: bool = Field(default=False, env="RELOAD_ON_CHANGE")
    enable_docs: bool = Field(default=True, env="ENABLE_DOCS")
    
    # Allowed hosts for CORS and security
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1", "vocelio.ai", "*.vocelio.ai"],
        env="ALLOWED_HOSTS"
    )
    
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "https://vocelio.ai", "https://*.vocelio.ai"],
        env="CORS_ORIGINS"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False

class AIModelConfig:
    """AI Model specific configurations"""
    
    # Conversation optimization settings
    CONVERSATION_OPTIMIZER = {
        "model_type": "transformer",
        "max_length": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    }
    
    # Sentiment analysis settings
    SENTIMENT_ANALYZER = {
        "model_type": "bert",
        "confidence_threshold": 0.8,
        "batch_size": 32,
        "max_sequence_length": 256
    }
    
    # Prediction model settings
    REVENUE_PREDICTOR = {
        "algorithm": "random_forest",
        "n_estimators": 100,
        "max_depth": 20,
        "min_samples_split": 5,
        "feature_importance_threshold": 0.01
    }
    
    # Neural network architectures
    NEURAL_ARCHITECTURES = {
        "conversation_optimizer": {
            "type": "transformer",
            "layers": 12,
            "hidden_size": 768,
            "attention_heads": 12,
            "dropout": 0.1
        },
        "sentiment_detector": {
            "type": "bert",
            "layers": 6,
            "hidden_size": 512,
            "attention_heads": 8,
            "dropout": 0.2
        },
        "outcome_predictor": {
            "type": "gpt",
            "layers": 24,
            "hidden_size": 1024,
            "attention_heads": 16,
            "dropout": 0.1
        }
    }

class OptimizationConfig:
    """Optimization configuration settings"""
    
    # Performance thresholds
    PERFORMANCE_THRESHOLDS = {
        "minimum_accuracy": 85.0,
        "target_accuracy": 95.0,
        "minimum_confidence": 0.8,
        "response_time_ms": 500,
        "success_rate_threshold": 30.0
    }
    
    # Optimization strategies
    OPTIMIZATION_STRATEGIES = {
        "voice_optimization": {
            "enabled": True,
            "confidence_threshold": 0.9,
            "min_data_points": 100,
            "testing_duration_hours": 24
        },
        "timing_optimization": {
            "enabled": True,
            "time_zone_consideration": True,
            "historical_data_days": 30,
            "minimum_improvement": 10.0
        },
        "script_optimization": {
            "enabled": True,
            "a_b_testing": True,
            "min_test_calls": 50,
            "significance_level": 0.05
        }
    }
    
    # Auto-optimization rules
    AUTO_OPTIMIZATION_RULES = {
        "enable_auto_apply": True,
        "confidence_threshold": 0.95,
        "max_simultaneous_optimizations": 5,
        "rollback_on_performance_drop": True,
        "performance_drop_threshold": 5.0
    }

class MonitoringConfig:
    """Monitoring and alerting configuration"""
    
    # Alert thresholds
    ALERT_THRESHOLDS = {
        "accuracy_drop_percentage": 5.0,
        "response_time_increase_ms": 200,
        "error_rate_threshold": 0.05,
        "resource_usage_threshold": 85.0
    }
    
    # Metrics collection
    METRICS_CONFIG = {
        "collection_interval_seconds": 60,
        "retention_days": 90,
        "aggregation_levels": ["1m", "5m", "1h", "24h"],
        "real_time_streaming": True
    }
    
    # Health check configuration
    HEALTH_CHECK_CONFIG = {
        "interval_seconds": 30,
        "timeout_seconds": 10,
        "failure_threshold": 3,
        "recovery_threshold": 2
    }

# Global configuration instance
_settings = None

def get_settings() -> AIBrainSettings:
    """Get configuration settings singleton"""
    global _settings
    if _settings is None:
        _settings = AIBrainSettings()
    return _settings

def get_model_config(model_name: str) -> Dict[str, Any]:
    """Get model-specific configuration"""
    return getattr(AIModelConfig, model_name.upper(), {})

def get_optimization_config() -> Dict[str, Any]:
    """Get optimization configuration"""
    return {
        "thresholds": OptimizationConfig.PERFORMANCE_THRESHOLDS,
        "strategies": OptimizationConfig.OPTIMIZATION_STRATEGIES,
        "auto_rules": OptimizationConfig.AUTO_OPTIMIZATION_RULES
    }

def get_monitoring_config() -> Dict[str, Any]:
    """Get monitoring configuration"""
    return {
        "alerts": MonitoringConfig.ALERT_THRESHOLDS,
        "metrics": MonitoringConfig.METRICS_CONFIG,
        "health_check": MonitoringConfig.HEALTH_CHECK_CONFIG
    }

# Environment-specific overrides
def apply_environment_overrides(settings: AIBrainSettings) -> AIBrainSettings:
    """Apply environment-specific configuration overrides"""
    
    if settings.environment == "production":
        # Production optimizations
        settings.debug_mode = False
        settings.enable_docs = False
        settings.real_time_optimization = True
        settings.performance_monitoring = True
        settings.log_level = "WARNING"
        settings.worker_processes = 8
        
    elif settings.environment == "staging":
        # Staging settings
        settings.debug_mode = False
        settings.enable_docs = True
        settings.log_level = "INFO"
        settings.worker_processes = 4
        
    elif settings.environment == "development":
        # Development settings
        settings.debug_mode = True
        settings.enable_docs = True
        settings.reload_on_change = True
        settings.log_level = "DEBUG"
        settings.worker_processes = 2
        
    return settings