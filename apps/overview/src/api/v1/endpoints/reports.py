"""
Reports Endpoints
Advanced reporting and analytics data export
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import json
import csv
import io
from uuid import uuid4

from services.reports_service import ReportsService, get_reports_service
from schemas.reports import (
    ReportRequest,
    ReportResponse,
    ReportStatus,
    ExportFormat,
    ScheduledReport
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()

@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    report_request: ReportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    reports_service: ReportsService = Depends(get_reports_service)
):
    """Generate a new report"""
    try:
        # Create report job
        report_id = await reports_service.create_report_job(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            request=report_request
        )
        
        # Add background task for report generation
        background_tasks.add_task(
            reports_service.generate_report_async,
            report_id,
            report_request
        )
        
        return ReportResponse(
            report_id=report_id,
            status=ReportStatus.PROCESSING,
            message="Report generation started",
            estimated_completion_time=datetime.utcnow() + timedelta(minutes=5),
            download_url=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/status/{report_id}", response_model=ReportResponse)
async def get_report_status(
    report_id: str,
    current_user: User = Depends(get_current_user),
    reports_service: ReportsService = Depends(get_reports_service)
):
    """Get report generation status"""
    try:
        status = await reports_service.get_report_status(report_id, current_user.organization_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report status: {str(e)}")

@router.get("/download/{report_id}")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    reports_service: ReportsService = Depends(get_reports_service)
):
    """Download completed report"""
    try:
        report_info = await reports_service.get_report_info(report_id, current_user.organization_id)
        
        if report_info.status != ReportStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Report is not ready for download")
        
        file_path = await reports_service.get_report_file_path(report_id)
        
        return FileResponse(
            path=file_path,
            filename=f"vocelio_report_{report_id}.{report_info.format.lower()}",
            media_type=reports_service.get_media_type(report_info.format)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download report: {str(e)}")

@router.get("/list", response_model=List[ReportResponse])
async def list_reports(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[ReportStatus] = None,
    current_user: User = Depends(get_current_user),
    reports_service: ReportsService = Depends(get_reports_service)
):
    """List user's reports with pagination"""
    try:
        reports = await reports_service.list_user_reports(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            status_filter=status_filter
        )
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")

@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    reports_service: ReportsService = Depends(get_reports_service)
):
    """Delete a report"""
    try:
        await reports_service.delete_report(report_id, current_user.organization_id)
        return {"message": "Report deleted successfully", "report_id": report_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")

@router.post("/export/dashboard-data")
async def export_dashboard_data(
    format: ExportFormat = ExportFormat.CSV,
    time_range: str = Query("30d", description="Time range: 1h, 24h, 7d, 30d, 90d"),
    include_charts: bool = False,
    current_user: User = Depends(get_current_user),
    reports_service: ReportsService = Depends(get_reports_service)
):
    """Export dashboard data in specified format"""
    try:
        if format == ExportFormat.CSV:
            return await export_dashboard_csv(current_user, reports_service, time_range)
        elif format == ExportFormat.EXCEL:
            return await export_dashboard_excel(current_user, reports_service, time_range, include_charts)
        elif format == ExportFormat.PDF:
            return await export_dashboard_pdf(current_user, reports_service, time_range, include_charts)
        else:
            return await export_dashboard_json(current_user, reports_service, time_range)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export dashboard data: {str(e)}")

async def export_dashboard_csv(user: User, service: ReportsService, time_range: str):
    """Export dashboard data as CSV"""
    data = await service.get_dashboard_export_data(user.organization_id, time_range)
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
    writer.writeheader()
    writer.writerows(data)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=dashboard_data_{time_range}.csv"}
    )

async def export_dashboard_excel(user: User, service: ReportsService, time_range: str, include_charts: bool):
    """Export dashboard data as Excel"""
    file_path = await service.create_excel_export(user.organization_id, time_range, include_charts)
    
    return FileResponse(
        path=file_path,
        filename=f"dashboard_data_{time_range}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

async def export_dashboard_pdf(user: User, service: ReportsService, time_range: str, include_charts: bool):
    """Export dashboard data as PDF"""
    file_path = await service.create_pdf_export(user.organization_id, time_range, include_charts)
    
    return FileResponse(
        path=file_path,
        filename=f"dashboard_report_{time_range}.pdf",
        media_type="application/pdf"
    )

async def export_dashboard_json(user: User, service: ReportsService, time_range: str):
    """Export dashboard data as JSON"""
    data = await service.get_comprehensive_dashboard_data(user.organization_id, time_range)
    
    return StreamingResponse(
        io.BytesIO(json.dumps(data, indent=2, default=str).encode('utf-8')),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=dashboard_data_{time_range}.json"}
    )

@router.post("/schedule", response_model=ScheduledReport)
async def schedule_report(
    schedule_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    reports_service: ReportsService = Depends(get_reports_service)
):
    """Schedule recurring report generation"""
    try:
        scheduled_report = await reports_service.schedule_report(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            schedule_config=schedule_request
        )
        return scheduled_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule report: {str(e)}")

@router.get("/scheduled", response_model=List[ScheduledReport])
async def list_scheduled_reports(
    current_user: User = Depends(get_current_user),
    reports_service: ReportsService = Depends(get_reports_service)
):
    """List scheduled reports"""
    try:
        reports = await reports_service.list_scheduled_reports(
            organization_id=current_user.organization_id,
            user_id=current_user.id
        )
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list scheduled reports: {str(e)}")

@router.delete("/scheduled/{schedule_id}")
async def cancel_scheduled_report(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    reports_service: ReportsService = Depends(get_reports_service)
):
    """Cancel scheduled report"""
    try:
        await reports_service.cancel_scheduled_report(schedule_id, current_user.organization_id)
        return {"message": "Scheduled report cancelled", "schedule_id": schedule_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel scheduled report: {str(e)}")

@router.get("/templates")
async def get_report_templates(
    category: Optional[str] = None,
    reports_service: ReportsService = Depends(get_reports_service)
):
    """Get available report templates"""
    try:
        templates = await reports_service.get_report_templates(category)
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report templates: {str(e)}")

@router.post("/templates/{template_id}/generate", response_model=ReportResponse)
async def generate_from_template(
    template_id: str,
    parameters: Dict[str, Any] = {},
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    reports_service: ReportsService = Depends(get_reports_service)
):
    """Generate report from template"""
    try:
        report_id = await reports_service.generate_from_template(
            template_id=template_id,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            parameters=parameters
        )
        
        background_tasks.add_task(
            reports_service.generate_template_report_async,
            report_id,
            template_id,
            parameters
        )
        
        return ReportResponse(
            report_id=report_id,
            status=ReportStatus.PROCESSING,
            message="Template report generation started",
            estimated_completion_time=datetime.utcnow() + timedelta(minutes=3)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report from template: {str(e)}")

@router.get("/analytics/summary")
async def get_analytics_summary(
    time_range: str = Query("30d"),
    current_user: User = Depends(get_current_user),
    reports_service: ReportsService = Depends(get_reports_service)
):
    """Get analytics summary for reporting"""
    try:
        summary = await reports_service.get_analytics_summary(
            organization_id=current_user.organization_id,
            time_range=time_range
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics summary: {str(e)}")

@router.post("/custom-query")
async def execute_custom_query(
    query_config: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    reports_service: ReportsService = Depends(get_reports_service)
):
    """Execute custom data query for reporting"""
    try:
        query_id = str(uuid4())
        
        background_tasks.add_task(
            reports_service.execute_custom_query_async,
            query_id,
            current_user.organization_id,
            query_config
        )
        
        return {
            "query_id": query_id,
            "status": "processing",
            "message": "Custom query execution started",
            "estimated_completion": "1-3 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute custom query: {str(e)}")
