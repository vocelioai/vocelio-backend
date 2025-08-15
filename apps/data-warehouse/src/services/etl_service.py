# apps/data-warehouse/src/services/etl_service.py
"""
ETL Service - Extract, Transform, Load operations
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from schemas.data_warehouse import *

logger = logging.getLogger(__name__)

class ETLService:
    """ETL pipeline management service"""
    
    def __init__(self):
        self.pipelines = {}
        self.running_pipelines = set()
        self.pipeline_runs = {}
        self.processing_active = False
        
    async def get_active_pipelines(self) -> int:
        """Get count of active pipelines"""
        return len([p for p in self.pipelines.values() if p.enabled])
    
    async def get_pipelines(self) -> List[ETLPipeline]:
        """Get all ETL pipelines"""
        return list(self.pipelines.values())
    
    async def create_pipeline(self, pipeline_data: ETLPipelineCreate) -> ETLPipeline:
        """Create new ETL pipeline"""
        pipeline_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        pipeline = ETLPipeline(
            id=pipeline_id,
            name=pipeline_data.name,
            description=pipeline_data.description,
            source_id=pipeline_data.source_id,
            transformation_rules=pipeline_data.transformation_rules,
            schedule=pipeline_data.schedule,
            enabled=pipeline_data.enabled,
            status=ETLStatus.PENDING,
            created_at=now,
            updated_at=now,
            last_run=None,
            next_run=None,
            records_processed=0,
            success_rate=0.0
        )
        
        self.pipelines[pipeline_id] = pipeline
        logger.info(f"Created ETL pipeline: {pipeline_data.name}")
        return pipeline
    
    async def get_pipeline(self, pipeline_id: str) -> Optional[ETLPipeline]:
        """Get pipeline by ID"""
        return self.pipelines.get(pipeline_id)
    
    async def update_pipeline(self, pipeline_id: str, update: ETLPipelineUpdate) -> Optional[ETLPipeline]:
        """Update pipeline"""
        if pipeline_id not in self.pipelines:
            return None
            
        pipeline = self.pipelines[pipeline_id]
        update_data = update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(pipeline, field, value)
        
        pipeline.updated_at = datetime.utcnow()
        return pipeline
    
    async def run_pipeline(self, pipeline_id: str) -> bool:
        """Run pipeline manually"""
        if pipeline_id not in self.pipelines:
            return False
            
        pipeline = self.pipelines[pipeline_id]
        if pipeline_id in self.running_pipelines:
            logger.warning(f"Pipeline {pipeline_id} is already running")
            return False
        
        self.running_pipelines.add(pipeline_id)
        pipeline.status = ETLStatus.RUNNING
        pipeline.last_run = datetime.utcnow()
        
        try:
            # Simulate ETL processing
            logger.info(f"Running ETL pipeline: {pipeline.name}")
            await asyncio.sleep(5)  # Simulate processing time
            
            # Update pipeline stats
            pipeline.records_processed += 1000  # Simulate processed records
            pipeline.status = ETLStatus.COMPLETED
            pipeline.success_rate = min(100.0, pipeline.success_rate + 1.0)
            
            logger.info(f"ETL pipeline completed: {pipeline.name}")
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {pipeline.name} - {e}")
            pipeline.status = ETLStatus.FAILED
            
        finally:
            self.running_pipelines.discard(pipeline_id)
            
        return True
    
    async def pause_pipeline(self, pipeline_id: str) -> bool:
        """Pause pipeline"""
        if pipeline_id not in self.pipelines:
            return False
            
        pipeline = self.pipelines[pipeline_id]
        pipeline.status = ETLStatus.PAUSED
        pipeline.enabled = False
        return True
    
    async def resume_pipeline(self, pipeline_id: str) -> bool:
        """Resume pipeline"""
        if pipeline_id not in self.pipelines:
            return False
            
        pipeline = self.pipelines[pipeline_id]
        pipeline.status = ETLStatus.PENDING
        pipeline.enabled = True
        return True
    
    async def start_continuous_processing(self):
        """Start continuous ETL processing"""
        self.processing_active = True
        logger.info("Starting continuous ETL processing")
        
        while self.processing_active:
            try:
                # Process scheduled pipelines
                for pipeline in self.pipelines.values():
                    if (pipeline.enabled and 
                        pipeline.status == ETLStatus.PENDING and 
                        pipeline.id not in self.running_pipelines):
                        
                        # Simple scheduling logic - run every 5 minutes for demo
                        if (not pipeline.last_run or 
                            datetime.utcnow() - pipeline.last_run > timedelta(minutes=5)):
                            asyncio.create_task(self.run_pipeline(pipeline.id))
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in continuous processing: {e}")
                await asyncio.sleep(60)
    
    async def stop_processing(self):
        """Stop continuous processing"""
        self.processing_active = False
        logger.info("Stopping ETL processing")
    
    async def count_active_pipelines(self) -> int:
        """Count active pipelines"""
        return len([p for p in self.pipelines.values() if p.enabled and p.status != ETLStatus.FAILED])
    
    async def get_processing_rate(self) -> int:
        """Get records processed per hour"""
        total_records = sum(p.records_processed for p in self.pipelines.values())
        # Simulate hourly rate
        return min(50000, total_records)
    
    async def get_success_rate(self) -> float:
        """Get pipeline success rate"""
        if not self.pipelines:
            return 0.0
        return sum(p.success_rate for p in self.pipelines.values()) / len(self.pipelines)
    
    async def count_recent_errors(self) -> int:
        """Count recent errors in last 24 hours"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        return len([p for p in self.pipelines.values() 
                   if p.status == ETLStatus.FAILED and 
                   p.last_run and p.last_run > cutoff])
    
    async def get_recent_activity(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent pipeline activity"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        activities = []
        for pipeline in self.pipelines.values():
            if pipeline.last_run and pipeline.last_run > cutoff:
                activities.append({
                    "pipeline_id": pipeline.id,
                    "pipeline_name": pipeline.name,
                    "status": pipeline.status.value,
                    "records_processed": pipeline.records_processed,
                    "timestamp": pipeline.last_run.isoformat()
                })
        
        # Sort by timestamp descending
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities
    
    async def get_engine_status(self) -> Dict[str, Any]:
        """Get ETL engine status"""
        return {
            "status": "healthy",
            "processing_active": self.processing_active,
            "running_pipelines": len(self.running_pipelines),
            "total_pipelines": len(self.pipelines),
            "memory_usage_mb": 256,  # Simulated
            "cpu_usage_percent": 15.2  # Simulated
        }
    
    async def run_maintenance(self):
        """Run ETL maintenance tasks"""
        logger.info("Running ETL maintenance")
        
        # Cleanup old pipeline runs
        cutoff = datetime.utcnow() - timedelta(days=30)
        cleaned = 0
        
        for pipeline in self.pipelines.values():
            if pipeline.last_run and pipeline.last_run < cutoff:
                # Reset old runs for demo
                cleaned += 1
        
        logger.info(f"ETL maintenance completed. Cleaned {cleaned} old runs")
