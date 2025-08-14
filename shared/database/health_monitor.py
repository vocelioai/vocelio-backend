# Database Health Monitoring Utilities for Vocelio Services
import asyncio
import asyncpg
import redis
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class DatabaseHealthCheck:
    """Database health check result"""
    status: HealthStatus
    response_time_ms: float
    active_connections: int = 0
    max_connections: int = 0
    error_message: Optional[str] = None
    last_check: Optional[datetime] = None
    
    def __post_init__(self):
        if self.last_check is None:
            self.last_check = datetime.utcnow()

class DatabaseHealthMonitor:
    """
    Comprehensive database health monitoring for PostgreSQL and Redis
    """
    
    def __init__(self, postgres_url: Optional[str] = None, redis_url: Optional[str] = None):
        self.postgres_url = postgres_url
        self.redis_url = redis_url
        self.pg_pool = None
        self.redis_client = None
        self.health_history: List[Dict[str, Any]] = []
        self.max_history = 100
        
    async def initialize_connections(self):
        """Initialize database connections"""
        try:
            # Initialize PostgreSQL pool
            if self.postgres_url:
                self.pg_pool = await asyncpg.create_pool(
                    self.postgres_url,
                    min_size=2,
                    max_size=10,
                    max_queries=50000,
                    max_inactive_connection_lifetime=300,
                    command_timeout=30
                )
                logger.info("✅ PostgreSQL connection pool initialized")
            
            # Initialize Redis client  
            if self.redis_url:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
                # Test Redis connection
                await asyncio.to_thread(self.redis_client.ping)
                logger.info("✅ Redis connection initialized")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize database connections: {e}")
            raise
    
    async def check_postgres_health(self) -> DatabaseHealthCheck:
        """Check PostgreSQL database health"""
        if not self.pg_pool:
            return DatabaseHealthCheck(
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                error_message="PostgreSQL pool not initialized"
            )
        
        try:
            start_time = time.time()
            
            async with self.pg_pool.acquire() as conn:
                # Basic connectivity test
                await conn.execute("SELECT 1")
                
                # Get connection stats
                pool_stats = {
                    "size": self.pg_pool.get_size(),
                    "idle": self.pg_pool.get_idle_size(),
                    "max_size": self.pg_pool.get_max_size(),
                    "min_size": self.pg_pool.get_min_size()
                }
                
                # Check for long-running queries (optional)
                long_queries = await conn.fetch("""
                    SELECT count(*) as count
                    FROM pg_stat_activity 
                    WHERE state = 'active' 
                    AND query_start < NOW() - INTERVAL '1 minute'
                    AND query NOT LIKE '%pg_stat_activity%'
                """)
                
                # Database performance check
                db_stats = await conn.fetchrow("""
                    SELECT 
                        numbackends as active_connections,
                        xact_commit + xact_rollback as total_transactions,
                        blks_read + blks_hit as total_blocks_accessed,
                        CASE 
                            WHEN blks_read + blks_hit > 0 
                            THEN round((blks_hit::float / (blks_read + blks_hit)) * 100, 2)
                            ELSE 0 
                        END as cache_hit_ratio
                    FROM pg_stat_database 
                    WHERE datname = current_database()
                """)
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine health status
            if response_time > 1000:  # > 1 second
                status = HealthStatus.DEGRADED
            elif len(long_queries) > 0 and long_queries[0]['count'] > 5:
                status = HealthStatus.DEGRADED  
            elif pool_stats["idle"] < 2:  # Low available connections
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return DatabaseHealthCheck(
                status=status,
                response_time_ms=round(response_time, 2),
                active_connections=db_stats['active_connections'] if db_stats else 0,
                max_connections=pool_stats["max_size"]
            )
            
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return DatabaseHealthCheck(
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                error_message=str(e)
            )
    
    async def check_redis_health(self) -> DatabaseHealthCheck:
        """Check Redis health"""
        if not self.redis_client:
            return DatabaseHealthCheck(
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                error_message="Redis client not initialized"
            )
        
        try:
            start_time = time.time()
            
            # Basic connectivity test
            await asyncio.to_thread(self.redis_client.ping)
            
            # Basic Redis connectivity and timing test
            response_time = (time.time() - start_time) * 1000
            
            # For now, just verify connectivity - Redis info can be added later
            # TODO: Enhance with Redis info metrics when async handling is resolved
            
            # Determine health status based on response time
            if response_time > 500:  # > 500ms
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return DatabaseHealthCheck(
                status=status,
                response_time_ms=round(response_time, 2),
                active_connections=1,  # Basic assumption - connected
                max_connections=0  # Will enhance later
            )
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return DatabaseHealthCheck(
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                error_message=str(e)
            )
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive database health check"""
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "databases": {},
            "overall_status": HealthStatus.HEALTHY
        }
        
        # Check PostgreSQL
        if self.postgres_url:
            pg_health = await self.check_postgres_health()
            health_data["databases"]["postgresql"] = {
                "status": pg_health.status,
                "response_time_ms": pg_health.response_time_ms,
                "active_connections": pg_health.active_connections,
                "max_connections": pg_health.max_connections,
                "error": pg_health.error_message,
                "last_check": pg_health.last_check.isoformat()
            }
            
            if pg_health.status == HealthStatus.UNHEALTHY:
                health_data["overall_status"] = HealthStatus.UNHEALTHY
            elif pg_health.status == HealthStatus.DEGRADED and health_data["overall_status"] == HealthStatus.HEALTHY:
                health_data["overall_status"] = HealthStatus.DEGRADED
        
        # Check Redis
        if self.redis_url:
            redis_health = await self.check_redis_health()
            health_data["databases"]["redis"] = {
                "status": redis_health.status,
                "response_time_ms": redis_health.response_time_ms,
                "active_connections": redis_health.active_connections,
                "max_connections": redis_health.max_connections,
                "error": redis_health.error_message,
                "last_check": redis_health.last_check.isoformat()
            }
            
            if redis_health.status == HealthStatus.UNHEALTHY:
                health_data["overall_status"] = HealthStatus.UNHEALTHY
            elif redis_health.status == HealthStatus.DEGRADED and health_data["overall_status"] == HealthStatus.HEALTHY:
                health_data["overall_status"] = HealthStatus.DEGRADED
        
        # Store in history
        self._store_health_record(health_data)
        
        return health_data
    
    def _store_health_record(self, health_data: Dict[str, Any]):
        """Store health check record in history"""
        self.health_history.append(health_data)
        
        # Trim history if too long
        if len(self.health_history) > self.max_history:
            self.health_history = self.health_history[-self.max_history:]
    
    def get_health_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get health history for specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            record for record in self.health_history
            if datetime.fromisoformat(record["timestamp"]) > cutoff_time
        ]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary statistics"""
        if not self.health_history:
            return {"message": "No health data available"}
        
        # Last 24 hours
        recent_records = self.get_health_history(24)
        
        if not recent_records:
            return {"message": "No recent health data"}
        
        # Calculate statistics
        total_checks = len(recent_records)
        healthy_checks = len([r for r in recent_records if r["overall_status"] == HealthStatus.HEALTHY])
        degraded_checks = len([r for r in recent_records if r["overall_status"] == HealthStatus.DEGRADED])
        unhealthy_checks = len([r for r in recent_records if r["overall_status"] == HealthStatus.UNHEALTHY])
        
        return {
            "period": "last_24_hours",
            "total_checks": total_checks,
            "healthy_checks": healthy_checks,
            "degraded_checks": degraded_checks,
            "unhealthy_checks": unhealthy_checks,
            "healthy_percentage": round((healthy_checks / total_checks) * 100, 1),
            "degraded_percentage": round((degraded_checks / total_checks) * 100, 1),
            "unhealthy_percentage": round((unhealthy_checks / total_checks) * 100, 1),
            "current_status": recent_records[-1]["overall_status"],
            "last_check": recent_records[-1]["timestamp"]
        }
    
    async def close_connections(self):
        """Close database connections"""
        try:
            if self.pg_pool:
                await self.pg_pool.close()
                logger.info("🔒 PostgreSQL pool closed")
            
            if self.redis_client:
                await asyncio.to_thread(self.redis_client.close)
                logger.info("🔒 Redis connection closed")
                
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


# Utility function for adding database health endpoints to FastAPI apps
def add_database_health_endpoints(app, db_monitor: DatabaseHealthMonitor):
    """Add database health endpoints to FastAPI app"""
    
    @app.get("/health/database")
    async def database_health():
        """Get database health status"""
        return await db_monitor.comprehensive_health_check()
    
    @app.get("/health/database/postgresql")
    async def postgresql_health():
        """Get PostgreSQL health status"""
        if not db_monitor.postgres_url:
            return {"error": "PostgreSQL not configured"}
        return await db_monitor.check_postgres_health()
    
    @app.get("/health/database/redis")
    async def redis_health():
        """Get Redis health status"""
        if not db_monitor.redis_url:
            return {"error": "Redis not configured"}
        return await db_monitor.check_redis_health()
    
    @app.get("/health/database/history")
    async def database_health_history(hours: int = 1):
        """Get database health history"""
        return {
            "history": db_monitor.get_health_history(hours),
            "summary": db_monitor.get_health_summary()
        }


# Example usage in a FastAPI service
"""
import os
from fastapi import FastAPI
from database_health import DatabaseHealthMonitor, add_database_health_endpoints

app = FastAPI(title="My Vocelio Service")

# Initialize database health monitor
db_monitor = DatabaseHealthMonitor(
    postgres_url=os.getenv("DATABASE_URL"),
    redis_url=os.getenv("REDIS_URL")
)

@app.on_event("startup")
async def startup():
    await db_monitor.initialize_connections()

@app.on_event("shutdown")
async def shutdown():
    await db_monitor.close_connections()

# Add database health endpoints
add_database_health_endpoints(app, db_monitor)

# Enhanced main health endpoint that includes database status
@app.get("/health")
async def enhanced_health_check():
    db_health = await db_monitor.comprehensive_health_check()
    
    return {
        "status": "healthy" if db_health["overall_status"] == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "my-service",
        "database": db_health,
        # ... other health checks
    }
"""
