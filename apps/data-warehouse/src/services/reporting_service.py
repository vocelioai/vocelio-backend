# apps/data-warehouse/src/services/reporting_service.py
"""
Reporting Service - Custom reports and scheduled reporting
"""

import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from schemas.data_warehouse import *

logger = logging.getLogger(__name__)

class ReportingService:
    """Custom reporting service"""
    
    def __init__(self):
        self.reports = {}
        self.executions = {}
        self._create_default_reports()
        
    def _create_default_reports(self):
        """Create default reports"""
        default_reports = [
            {
                "name": "Daily Operations Summary",
                "description": "Daily summary of call center operations",
                "query": "SELECT DATE(created_at) as date, COUNT(*) as total_calls, AVG(duration) as avg_duration, SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as successful_calls FROM calls WHERE created_at >= CURRENT_DATE - INTERVAL '7 days' GROUP BY DATE(created_at) ORDER BY date DESC",
                "parameters": {},
                "schedule": "0 8 * * *",  # Daily at 8 AM
                "enabled": True
            },
            {
                "name": "Weekly Lead Performance",
                "description": "Weekly analysis of lead generation and conversion",
                "query": "SELECT status, COUNT(*) as count, AVG(score) as avg_score FROM leads WHERE created_at >= CURRENT_DATE - INTERVAL '7 days' GROUP BY status",
                "parameters": {},
                "schedule": "0 9 * * 1",  # Monday at 9 AM
                "enabled": True
            },
            {
                "name": "Agent Performance Report",
                "description": "Individual agent performance metrics",
                "query": "SELECT agent_id, COUNT(*) as total_calls, AVG(duration) as avg_duration, AVG(rating) as avg_rating FROM calls WHERE created_at >= '{start_date}' AND created_at <= '{end_date}' GROUP BY agent_id ORDER BY total_calls DESC",
                "parameters": {"start_date": "2024-11-01", "end_date": "2024-11-30"},
                "schedule": None,
                "enabled": True
            },
            {
                "name": "Campaign ROI Dashboard",
                "description": "Campaign return on investment analysis",
                "query": "SELECT c.name, c.budget, COUNT(l.id) as leads_generated, SUM(l.value) as total_revenue, (SUM(l.value) - c.budget) / c.budget * 100 as roi_percent FROM campaigns c LEFT JOIN leads l ON c.id = l.campaign_id WHERE c.created_at >= '{start_date}' GROUP BY c.id, c.name, c.budget ORDER BY roi_percent DESC",
                "parameters": {"start_date": "2024-10-01"},
                "schedule": "0 10 1 * *",  # Monthly on 1st at 10 AM
                "enabled": True
            }
        ]
        
        for report_data in default_reports:
            report_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            report = Report(
                id=report_id,
                name=report_data["name"],
                description=report_data["description"],
                query=report_data["query"],
                parameters=report_data["parameters"],
                schedule=report_data["schedule"],
                enabled=report_data["enabled"],
                created_at=now,
                updated_at=now,
                last_run=None,
                run_count=0
            )
            
            self.reports[report_id] = report
    
    async def get_reports(self) -> List[Report]:
        """Get all reports"""
        return list(self.reports.values())
    
    async def create_report(self, report_data: ReportCreate) -> Report:
        """Create new report"""
        report_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        report = Report(
            id=report_id,
            name=report_data.name,
            description=report_data.description,
            query=report_data.query,
            parameters=report_data.parameters,
            schedule=report_data.schedule,
            enabled=report_data.enabled,
            created_at=now,
            updated_at=now,
            last_run=None,
            run_count=0
        )
        
        self.reports[report_id] = report
        logger.info(f"Created report: {report_data.name}")
        return report
    
    async def get_report(self, report_id: str) -> Optional[Report]:
        """Get report by ID"""
        return self.reports.get(report_id)
    
    async def update_report(self, report_id: str, update: ReportUpdate) -> Optional[Report]:
        """Update report"""
        if report_id not in self.reports:
            return None
            
        report = self.reports[report_id]
        update_data = update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(report, field, value)
        
        report.updated_at = datetime.utcnow()
        return report
    
    async def run_report(self, report_id: str, parameters: Dict[str, Any] = {}) -> Optional[ReportExecution]:
        """Run report with optional parameters"""
        if report_id not in self.reports:
            return None
            
        report = self.reports[report_id]
        execution_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Merge default parameters with provided ones
            final_parameters = {**report.parameters, **parameters}
            
            # Simulate report execution
            logger.info(f"Running report: {report.name}")
            await asyncio.sleep(2)  # Simulate processing time
            
            # Generate sample report data
            sample_data = self._generate_report_data(report.name)
            
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            execution = ReportExecution(
                id=execution_id,
                report_id=report_id,
                status="completed",
                data=sample_data,
                parameters=final_parameters,
                execution_time_ms=execution_time,
                created_at=start_time
            )
            
            # Update report stats
            report.last_run = start_time
            report.run_count += 1
            
            # Store execution
            self.executions[execution_id] = execution
            
            logger.info(f"Report completed: {report.name} in {execution_time}ms")
            return execution
            
        except Exception as e:
            logger.error(f"Report failed: {report.name} - {e}")
            
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            execution = ReportExecution(
                id=execution_id,
                report_id=report_id,
                status="failed",
                data=[],
                parameters=parameters,
                execution_time_ms=execution_time,
                created_at=start_time
            )
            
            self.executions[execution_id] = execution
            return execution
    
    def _generate_report_data(self, report_name: str) -> List[Dict[str, Any]]:
        """Generate sample report data"""
        if "Daily Operations" in report_name:
            return [
                {"date": "2024-11-01", "total_calls": 1250, "avg_duration": 285, "successful_calls": 1180},
                {"date": "2024-11-02", "total_calls": 1180, "avg_duration": 292, "successful_calls": 1110},
                {"date": "2024-11-03", "total_calls": 1350, "avg_duration": 275, "successful_calls": 1285},
                {"date": "2024-11-04", "total_calls": 1420, "avg_duration": 301, "successful_calls": 1340},
                {"date": "2024-11-05", "total_calls": 1380, "avg_duration": 288, "successful_calls": 1295}
            ]
        
        elif "Lead Performance" in report_name:
            return [
                {"status": "new", "count": 450, "avg_score": 62.5},
                {"status": "contacted", "count": 320, "avg_score": 71.2},
                {"status": "qualified", "count": 180, "avg_score": 85.4},
                {"status": "converted", "count": 85, "avg_score": 92.1},
                {"status": "lost", "count": 95, "avg_score": 45.8}
            ]
        
        elif "Agent Performance" in report_name:
            return [
                {"agent_id": "AGT001", "total_calls": 145, "avg_duration": 320, "avg_rating": 4.7},
                {"agent_id": "AGT002", "total_calls": 138, "avg_duration": 285, "avg_rating": 4.5},
                {"agent_id": "AGT003", "total_calls": 152, "avg_duration": 340, "avg_rating": 4.8},
                {"agent_id": "AGT004", "total_calls": 129, "avg_duration": 295, "avg_rating": 4.4},
                {"agent_id": "AGT005", "total_calls": 141, "avg_duration": 315, "avg_rating": 4.6}
            ]
        
        elif "Campaign ROI" in report_name:
            return [
                {"name": "Solar Lead Gen Pro", "budget": 15000, "leads_generated": 250, "total_revenue": 45000, "roi_percent": 200.0},
                {"name": "Insurance Outreach", "budget": 12000, "leads_generated": 190, "total_revenue": 28000, "roi_percent": 133.3},
                {"name": "Tech Startup Leads", "budget": 20000, "leads_generated": 180, "total_revenue": 52000, "roi_percent": 160.0},
                {"name": "Real Estate Warm", "budget": 8000, "leads_generated": 120, "total_revenue": 18000, "roi_percent": 125.0}
            ]
        
        else:
            return [
                {"metric": "Sample Metric 1", "value": 100},
                {"metric": "Sample Metric 2", "value": 150},
                {"metric": "Sample Metric 3", "value": 120}
            ]
    
    async def get_report_executions(self, report_id: str, limit: int = 20) -> List[ReportExecution]:
        """Get report execution history"""
        executions = [e for e in self.executions.values() if e.report_id == report_id]
        executions.sort(key=lambda x: x.created_at, reverse=True)
        return executions[:limit]
    
    async def get_execution(self, execution_id: str) -> Optional[ReportExecution]:
        """Get specific report execution"""
        return self.executions.get(execution_id)
    
    async def delete_report(self, report_id: str) -> bool:
        """Delete report"""
        if report_id in self.reports:
            del self.reports[report_id]
            # Clean up executions
            execution_ids_to_remove = [eid for eid, e in self.executions.items() if e.report_id == report_id]
            for eid in execution_ids_to_remove:
                del self.executions[eid]
            return True
        return False
