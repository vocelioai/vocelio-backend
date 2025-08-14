# apps/overview/src/models/enhanced_overview.py
"""
Enhanced Overview Models - Merged from overview + overview-service
Combines structured dashboard management with real-time features
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

from shared.database.models import BaseModel

Base = declarative_base()

class DashboardWidget(BaseModel):
    """Dashboard widget configuration"""
    __tablename__ = "dashboard_widgets"
    
    id = Column(String, primary_key=True, default=lambda: f"widget_{uuid.uuid4().hex[:12]}")
    user_id = Column(String, nullable=False, index=True)
    organization_id = Column(String, nullable=False, index=True)
    widget_type = Column(String(50), nullable=False)  # metrics, chart, ai_insights, etc.
    title = Column(String(255), nullable=False)
    configuration = Column(JSON, default={})
    position = Column(JSON, default={})  # x, y, width, height
    is_visible = Column(Boolean, default=True)
    refresh_interval = Column(Integer, default=30)  # seconds
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class MetricsSnapshot(BaseModel):
    """Historical metrics snapshots for trending"""
    __tablename__ = "metrics_snapshots"
    
    id = Column(String, primary_key=True, default=lambda: f"snap_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String, nullable=False, index=True)
    snapshot_type = Column(String(50), nullable=False)  # hourly, daily, weekly
    
    # Core metrics
    total_calls = Column(Integer, default=0)
    successful_calls = Column(Integer, default=0)
    active_campaigns = Column(Integer, default=0)
    revenue_generated = Column(Float, default=0.0)
    
    # Performance metrics
    success_rate = Column(Float, default=0.0)
    ai_optimization_score = Column(Float, default=0.0)
    average_call_duration = Column(Float, default=0.0)
    
    # System metrics
    system_uptime = Column(Float, default=0.0)
    services_online = Column(Integer, default=0)
    
    # Additional data
    metrics_data = Column(JSON, default={})
    
    snapshot_time = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

class AIInsightRecord(BaseModel):
    """AI-generated insights and recommendations"""
    __tablename__ = "ai_insights"
    
    id = Column(String, primary_key=True, default=lambda: f"insight_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String, nullable=False, index=True)
    
    # Insight details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    insight_type = Column(String(50), nullable=False)  # optimization, alert, recommendation
    category = Column(String(50), nullable=False)  # voice, timing, targeting, etc.
    
    # Confidence and impact
    confidence_score = Column(Float, nullable=False)
    impact_estimate = Column(String(255))
    potential_value = Column(Float, default=0.0)
    
    # Priority and status
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="active")  # active, implemented, dismissed
    
    # Action details
    recommended_action = Column(JSON, default={})
    implementation_steps = Column(JSON, default=list)
    
    # Tracking
    is_implemented = Column(Boolean, default=False)
    implemented_at = Column(DateTime)
    implementation_result = Column(JSON, default={})
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SystemHealthLog(BaseModel):
    """System health monitoring logs"""
    __tablename__ = "system_health_logs"
    
    id = Column(String, primary_key=True, default=lambda: f"health_{uuid.uuid4().hex[:12]}")
    
    # Health metrics
    overall_status = Column(String(20), nullable=False)  # operational, degraded, down
    uptime_percentage = Column(Float, nullable=False)
    services_online = Column(Integer, nullable=False)
    total_services = Column(Integer, nullable=False)
    
    # Performance metrics
    response_time_avg = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    
    # Service status
    service_status = Column(JSON, default={})  # Individual service statuses
    
    # Alerts and issues
    active_alerts = Column(Integer, default=0)
    critical_issues = Column(JSON, default=list)
    
    check_time = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

class RevenueMetric(BaseModel):
    """Revenue tracking and analytics"""
    __tablename__ = "revenue_metrics"
    
    id = Column(String, primary_key=True, default=lambda: f"revenue_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String, nullable=False, index=True)
    
    # Time period
    period_type = Column(String(20), nullable=False)  # hourly, daily, weekly, monthly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Revenue data
    total_revenue = Column(Float, nullable=False)
    revenue_growth = Column(Float, default=0.0)
    
    # Revenue breakdown
    revenue_by_source = Column(JSON, default={})
    revenue_by_industry = Column(JSON, default={})
    revenue_by_campaign = Column(JSON, default={})
    
    # Projections
    projected_revenue = Column(Float, default=0.0)
    projection_confidence = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class DashboardAlert(BaseModel):
    """Dashboard alerts and notifications"""
    __tablename__ = "dashboard_alerts"
    
    id = Column(String, primary_key=True, default=lambda: f"alert_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)  # Null for organization-wide alerts
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # performance, revenue, system, ai_insight
    severity = Column(String(20), nullable=False)  # info, warning, error, critical
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Alert data
    related_data = Column(JSON, default={})
    action_required = Column(Boolean, default=False)
    action_url = Column(String(500))
    
    # Status
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    read_at = Column(DateTime)
    dismissed_at = Column(DateTime)

class LiveMetricsCache(BaseModel):
    """Cache for live metrics data"""
    __tablename__ = "live_metrics_cache"
    
    id = Column(String, primary_key=True, default=lambda: f"cache_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String, nullable=False, index=True)
    
    # Cached metrics data
    metrics_data = Column(JSON, nullable=False)
    
    # Cache metadata
    cache_key = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
