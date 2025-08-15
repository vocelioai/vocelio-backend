# apps/data-warehouse/src/schemas/data_warehouse.py
"""
Data Warehouse Service Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class DataSourceType(str, Enum):
    """Data source types"""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    WEBHOOK = "webhook"

class ETLStatus(str, Enum):
    """ETL pipeline status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class DataQuality(str, Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

# Data Source Schemas
class DataSourceBase(BaseModel):
    """Base data source schema"""
    name: str = Field(..., description="Data source name")
    type: DataSourceType = Field(..., description="Data source type")
    description: Optional[str] = Field(None, description="Data source description")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Source configuration")
    enabled: bool = Field(True, description="Whether source is enabled")

class DataSourceCreate(DataSourceBase):
    """Create data source schema"""
    pass

class DataSourceUpdate(BaseModel):
    """Update data source schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None

class DataSource(DataSourceBase):
    """Data source response schema"""
    id: str = Field(..., description="Data source ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_sync: Optional[datetime] = Field(None, description="Last sync timestamp")
    records_processed: int = Field(0, description="Total records processed")
    quality_score: float = Field(0.0, description="Data quality score (0-100)")

# ETL Pipeline Schemas
class ETLPipelineBase(BaseModel):
    """Base ETL pipeline schema"""
    name: str = Field(..., description="Pipeline name")
    description: Optional[str] = Field(None, description="Pipeline description")
    source_id: str = Field(..., description="Data source ID")
    transformation_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Transformation rules")
    schedule: Optional[str] = Field(None, description="Cron schedule")
    enabled: bool = Field(True, description="Whether pipeline is enabled")

class ETLPipelineCreate(ETLPipelineBase):
    """Create ETL pipeline schema"""
    pass

class ETLPipelineUpdate(BaseModel):
    """Update ETL pipeline schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    transformation_rules: Optional[List[Dict[str, Any]]] = None
    schedule: Optional[str] = None
    enabled: Optional[bool] = None

class ETLPipeline(ETLPipelineBase):
    """ETL pipeline response schema"""
    id: str = Field(..., description="Pipeline ID")
    status: ETLStatus = Field(..., description="Pipeline status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_run: Optional[datetime] = Field(None, description="Last execution timestamp")
    next_run: Optional[datetime] = Field(None, description="Next scheduled run")
    records_processed: int = Field(0, description="Total records processed")
    success_rate: float = Field(0.0, description="Success rate percentage")

# Data Lake Schemas
class DataLakeEntry(BaseModel):
    """Data lake entry schema"""
    id: str = Field(..., description="Entry ID")
    source_id: str = Field(..., description="Data source ID")
    pipeline_id: Optional[str] = Field(None, description="ETL pipeline ID")
    table_name: str = Field(..., description="Target table name")
    record_count: int = Field(..., description="Number of records")
    size_bytes: int = Field(..., description="Data size in bytes")
    quality: DataQuality = Field(..., description="Data quality assessment")
    created_at: datetime = Field(..., description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# Analytics Schemas
class AnalyticsQuery(BaseModel):
    """Analytics query schema"""
    query: str = Field(..., description="SQL query or analysis specification")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    format: str = Field("json", description="Output format (json, csv, parquet)")
    limit: Optional[int] = Field(None, description="Result limit")

class AnalyticsResult(BaseModel):
    """Analytics result schema"""
    query_id: str = Field(..., description="Query execution ID")
    status: str = Field(..., description="Execution status")
    data: List[Dict[str, Any]] = Field(..., description="Result data")
    metadata: Dict[str, Any] = Field(..., description="Result metadata")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")
    created_at: datetime = Field(..., description="Execution timestamp")

# Report Schemas
class ReportBase(BaseModel):
    """Base report schema"""
    name: str = Field(..., description="Report name")
    description: Optional[str] = Field(None, description="Report description")
    query: str = Field(..., description="Report query")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Default parameters")
    schedule: Optional[str] = Field(None, description="Report schedule")
    enabled: bool = Field(True, description="Whether report is enabled")

class ReportCreate(ReportBase):
    """Create report schema"""
    pass

class ReportUpdate(BaseModel):
    """Update report schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    query: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = None
    enabled: Optional[bool] = None

class Report(ReportBase):
    """Report response schema"""
    id: str = Field(..., description="Report ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_run: Optional[datetime] = Field(None, description="Last execution timestamp")
    run_count: int = Field(0, description="Total execution count")

class ReportExecution(BaseModel):
    """Report execution schema"""
    id: str = Field(..., description="Execution ID")
    report_id: str = Field(..., description="Report ID")
    status: str = Field(..., description="Execution status")
    data: List[Dict[str, Any]] = Field(..., description="Report data")
    parameters: Dict[str, Any] = Field(..., description="Execution parameters")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")
    created_at: datetime = Field(..., description="Execution timestamp")

# Dashboard Schemas
class DashboardMetrics(BaseModel):
    """Data warehouse dashboard metrics"""
    total_data_sources: int = Field(..., description="Total number of data sources")
    active_pipelines: int = Field(..., description="Number of active ETL pipelines")
    total_records: int = Field(..., description="Total records in data lake")
    storage_used_gb: float = Field(..., description="Storage used in GB")
    data_quality_avg: float = Field(..., description="Average data quality score")
    processing_rate_per_hour: int = Field(..., description="Records processed per hour")
    pipeline_success_rate: float = Field(..., description="Pipeline success rate")
    recent_errors: int = Field(..., description="Recent errors count")

# Health Check Schema
class HealthCheck(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Health check timestamp")
    environment: str = Field(..., description="Environment")
    data_sources: List[str] = Field(..., description="Connected data sources")
    active_pipelines: int = Field(..., description="Active pipelines count")
