# apps/data-warehouse/src/api/v1/api.py
"""
Data Warehouse Service API Router
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from schemas.data_warehouse import *
from services.etl_service import ETLService
from services.analytics_service import AnalyticsService  
from services.data_lake_service import DataLakeService
from services.reporting_service import ReportingService

api_router = APIRouter()

# Data Sources Endpoints
@api_router.get("/data-sources", response_model=List[DataSource])
async def get_data_sources(
    data_lake_service: DataLakeService = Depends()
):
    """Get all data sources"""
    return await data_lake_service.get_data_sources()

@api_router.post("/data-sources", response_model=DataSource)
async def create_data_source(
    data_source: DataSourceCreate,
    data_lake_service: DataLakeService = Depends()
):
    """Create new data source"""
    return await data_lake_service.create_data_source(data_source)

@api_router.get("/data-sources/{source_id}", response_model=DataSource)
async def get_data_source(
    source_id: str,
    data_lake_service: DataLakeService = Depends()
):
    """Get data source by ID"""
    source = await data_lake_service.get_data_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    return source

@api_router.put("/data-sources/{source_id}", response_model=DataSource)
async def update_data_source(
    source_id: str,
    data_source: DataSourceUpdate,
    data_lake_service: DataLakeService = Depends()
):
    """Update data source"""
    updated = await data_lake_service.update_data_source(source_id, data_source)
    if not updated:
        raise HTTPException(status_code=404, detail="Data source not found")
    return updated

@api_router.delete("/data-sources/{source_id}")
async def delete_data_source(
    source_id: str,
    data_lake_service: DataLakeService = Depends()
):
    """Delete data source"""
    deleted = await data_lake_service.delete_data_source(source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Data source not found")
    return {"message": "Data source deleted successfully"}

# ETL Pipelines Endpoints
@api_router.get("/pipelines", response_model=List[ETLPipeline])
async def get_pipelines(
    etl_service: ETLService = Depends()
):
    """Get all ETL pipelines"""
    return await etl_service.get_pipelines()

@api_router.post("/pipelines", response_model=ETLPipeline)
async def create_pipeline(
    pipeline: ETLPipelineCreate,
    etl_service: ETLService = Depends()
):
    """Create new ETL pipeline"""
    return await etl_service.create_pipeline(pipeline)

@api_router.get("/pipelines/{pipeline_id}", response_model=ETLPipeline)
async def get_pipeline(
    pipeline_id: str,
    etl_service: ETLService = Depends()
):
    """Get pipeline by ID"""
    pipeline = await etl_service.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline

@api_router.put("/pipelines/{pipeline_id}", response_model=ETLPipeline)
async def update_pipeline(
    pipeline_id: str,
    pipeline: ETLPipelineUpdate,
    etl_service: ETLService = Depends()
):
    """Update pipeline"""
    updated = await etl_service.update_pipeline(pipeline_id, pipeline)
    if not updated:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return updated

@api_router.post("/pipelines/{pipeline_id}/run")
async def run_pipeline(
    pipeline_id: str,
    background_tasks: BackgroundTasks,
    etl_service: ETLService = Depends()
):
    """Run pipeline manually"""
    background_tasks.add_task(etl_service.run_pipeline, pipeline_id)
    return {"message": "Pipeline execution started", "pipeline_id": pipeline_id}

@api_router.post("/pipelines/{pipeline_id}/pause")
async def pause_pipeline(
    pipeline_id: str,
    etl_service: ETLService = Depends()
):
    """Pause pipeline"""
    paused = await etl_service.pause_pipeline(pipeline_id)
    if not paused:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"message": "Pipeline paused successfully"}

@api_router.post("/pipelines/{pipeline_id}/resume")
async def resume_pipeline(
    pipeline_id: str,
    etl_service: ETLService = Depends()
):
    """Resume pipeline"""
    resumed = await etl_service.resume_pipeline(pipeline_id)
    if not resumed:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"message": "Pipeline resumed successfully"}

# Data Lake Endpoints
@api_router.get("/data-lake/entries", response_model=List[DataLakeEntry])
async def get_data_lake_entries(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    data_lake_service: DataLakeService = Depends()
):
    """Get data lake entries"""
    return await data_lake_service.get_entries(limit=limit, offset=offset)

@api_router.get("/data-lake/tables")
async def get_data_lake_tables(
    data_lake_service: DataLakeService = Depends()
):
    """Get available data lake tables"""
    return await data_lake_service.get_tables()

@api_router.get("/data-lake/schema/{table_name}")
async def get_table_schema(
    table_name: str,
    data_lake_service: DataLakeService = Depends()
):
    """Get table schema"""
    schema = await data_lake_service.get_table_schema(table_name)
    if not schema:
        raise HTTPException(status_code=404, detail="Table not found")
    return schema

@api_router.get("/data-lake/preview/{table_name}")
async def preview_table_data(
    table_name: str,
    limit: int = Query(10, ge=1, le=100),
    data_lake_service: DataLakeService = Depends()
):
    """Preview table data"""
    data = await data_lake_service.preview_table(table_name, limit=limit)
    if not data:
        raise HTTPException(status_code=404, detail="Table not found")
    return data

# Analytics Endpoints
@api_router.post("/analytics/query", response_model=AnalyticsResult)
async def execute_analytics_query(
    query: AnalyticsQuery,
    analytics_service: AnalyticsService = Depends()
):
    """Execute analytics query"""
    return await analytics_service.execute_query(query)

@api_router.get("/analytics/queries")
async def get_query_history(
    limit: int = Query(50, ge=1, le=200),
    analytics_service: AnalyticsService = Depends()
):
    """Get query execution history"""
    return await analytics_service.get_query_history(limit=limit)

@api_router.get("/analytics/templates")
async def get_query_templates(
    analytics_service: AnalyticsService = Depends()
):
    """Get predefined query templates"""
    return await analytics_service.get_query_templates()

# Reports Endpoints
@api_router.get("/reports", response_model=List[Report])
async def get_reports(
    reporting_service: ReportingService = Depends()
):
    """Get all reports"""
    return await reporting_service.get_reports()

@api_router.post("/reports", response_model=Report)
async def create_report(
    report: ReportCreate,
    reporting_service: ReportingService = Depends()
):
    """Create new report"""
    return await reporting_service.create_report(report)

@api_router.get("/reports/{report_id}", response_model=Report)
async def get_report(
    report_id: str,
    reporting_service: ReportingService = Depends()
):
    """Get report by ID"""
    report = await reporting_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@api_router.post("/reports/{report_id}/run", response_model=ReportExecution)
async def run_report(
    report_id: str,
    parameters: Dict[str, Any] = {},
    reporting_service: ReportingService = Depends()
):
    """Run report with optional parameters"""
    execution = await reporting_service.run_report(report_id, parameters)
    if not execution:
        raise HTTPException(status_code=404, detail="Report not found")
    return execution

@api_router.get("/reports/{report_id}/executions")
async def get_report_executions(
    report_id: str,
    limit: int = Query(20, ge=1, le=100),
    reporting_service: ReportingService = Depends()
):
    """Get report execution history"""
    return await reporting_service.get_report_executions(report_id, limit=limit)

# Dashboard Endpoints
@api_router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    data_lake_service: DataLakeService = Depends(),
    etl_service: ETLService = Depends(),
    analytics_service: AnalyticsService = Depends()
):
    """Get data warehouse dashboard metrics"""
    return {
        "total_data_sources": await data_lake_service.count_data_sources(),
        "active_pipelines": await etl_service.count_active_pipelines(),
        "total_records": await data_lake_service.count_total_records(),
        "storage_used_gb": await data_lake_service.get_storage_usage(),
        "data_quality_avg": await data_lake_service.get_average_quality_score(),
        "processing_rate_per_hour": await etl_service.get_processing_rate(),
        "pipeline_success_rate": await etl_service.get_success_rate(),
        "recent_errors": await etl_service.count_recent_errors()
    }

@api_router.get("/dashboard/activity")
async def get_recent_activity(
    hours: int = Query(24, ge=1, le=168),  # Max 1 week
    etl_service: ETLService = Depends()
):
    """Get recent activity"""
    return await etl_service.get_recent_activity(hours=hours)

@api_router.get("/dashboard/quality")
async def get_data_quality_overview(
    data_lake_service: DataLakeService = Depends()
):
    """Get data quality overview"""
    return await data_lake_service.get_quality_overview()

# System Endpoints
@api_router.get("/system/status")
async def get_system_status(
    etl_service: ETLService = Depends(),
    data_lake_service: DataLakeService = Depends()
):
    """Get system status"""
    return {
        "etl_engine": await etl_service.get_engine_status(),
        "data_lake": await data_lake_service.get_storage_status(),
        "timestamp": datetime.utcnow().isoformat()
    }

@api_router.post("/system/maintenance")
async def trigger_maintenance(
    background_tasks: BackgroundTasks,
    etl_service: ETLService = Depends(),
    data_lake_service: DataLakeService = Depends()
):
    """Trigger system maintenance"""
    background_tasks.add_task(etl_service.run_maintenance)
    background_tasks.add_task(data_lake_service.run_cleanup)
    return {"message": "Maintenance tasks started"}
