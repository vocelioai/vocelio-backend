"""
Analytics Database Models
📊 SQLAlchemy models for analytics data storage
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from shared.database.models import BaseModel

Base = declarative_base()

class AnalyticsModel(BaseModel):
    """Base analytics model with common fields"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class CallMetrics(AnalyticsModel):
    """Call metrics data model"""
    __tablename__ = "call_metrics"
    
    # Time dimensions
    date = Column(DateTime, nullable=False, index=True)
    hour = Column(Integer, nullable=False, index=True)  # 0-23
    day_of_week = Column(Integer, nullable=False)  # 0-6 (Monday=0)
    
    # Call volume metrics
    total_calls = Column(Integer, default=0, nullable=False)
    successful_calls = Column(Integer, default=0, nullable=False)
    failed_calls = Column(Integer, default=0, nullable=False)
    abandoned_calls = Column(Integer, default=0, nullable=False)
    
    # Performance metrics
    success_rate = Column(Float, default=0.0, nullable=False)
    avg_duration = Column(Float, default=0.0, nullable=False)  # seconds
    avg_wait_time = Column(Float, default=0.0, nullable=False)  # seconds
    
    # Revenue metrics
    revenue_generated = Column(Float, default=0.0, nullable=False)
    cost_incurred = Column(Float, default=0.0, nullable=False)
    
    # Quality metrics
    customer_satisfaction = Column(Float, default=0.0, nullable=False)  # 1-5 scale
    quality_score = Column(Float, default=0.0, nullable=False)  # 1-100 scale
    
    # Additional metadata
    campaign_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    agent_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    voice_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_call_metrics_org_date', 'organization_id', 'date'),
        Index('idx_call_metrics_org_hour', 'organization_id', 'date', 'hour'),
        Index('idx_call_metrics_campaign', 'campaign_id', 'date'),
        Index('idx_call_metrics_agent', 'agent_id', 'date'),
    )

class AgentMetrics(AnalyticsModel):
    """Agent performance metrics model"""
    __tablename__ = "agent_metrics"
    
    agent_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    agent_name = Column(String(255), nullable=False)
    
    # Time dimension
    date = Column(DateTime, nullable=False, index=True)
    
    # Call metrics
    total_calls = Column(Integer, default=0, nullable=False)
    successful_calls = Column(Integer, default=0, nullable=False)
    failed_calls = Column(Integer, default=0, nullable=False)
    
    # Performance metrics
    success_rate = Column(Float, default=0.0, nullable=False)
    avg_call_duration = Column(Float, default=0.0, nullable=False)
    avg_response_time = Column(Float, default=0.0, nullable=False)
    
    # Quality metrics
    customer_satisfaction = Column(Float, default=0.0, nullable=False)
    quality_score = Column(Float, default=0.0, nullable=False)
    performance_score = Column(Float, default=0.0, nullable=False)
    
    # Revenue metrics
    revenue_generated = Column(Float, default=0.0, nullable=False)
    leads_converted = Column(Integer, default=0, nullable=False)
    conversion_rate = Column(Float, default=0.0, nullable=False)
    
    # Availability metrics
    online_time = Column(Float, default=0.0, nullable=False)  # seconds
    idle_time = Column(Float, default=0.0, nullable=False)  # seconds
    break_time = Column(Float, default=0.0, nullable=False)  # seconds
    
    # Status tracking
    status = Column(String(50), default='active', nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_agent_metrics_org_date', 'organization_id', 'date'),
        Index('idx_agent_metrics_agent_date', 'agent_id', 'date'),
        Index('idx_agent_metrics_performance', 'organization_id', 'performance_score'),
    )

class CampaignMetrics(AnalyticsModel):
    """Campaign performance metrics model"""
    __tablename__ = "campaign_metrics"
    
    campaign_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    campaign_name = Column(String(255), nullable=False)
    campaign_type = Column(String(100), nullable=False)
    
    # Time dimension
    date = Column(DateTime, nullable=False, index=True)
    
    # Call metrics
    total_calls = Column(Integer, default=0, nullable=False)
    successful_calls = Column(Integer, default=0, nullable=False)
    failed_calls = Column(Integer, default=0, nullable=False)
    
    # Performance metrics
    success_rate = Column(Float, default=0.0, nullable=False) 
    conversion_rate = Column(Float, default=0.0, nullable=False)
    avg_call_duration = Column(Float, default=0.0, nullable=False)
    
    # Financial metrics
    total_cost = Column(Float, default=0.0, nullable=False)
    revenue_generated = Column(Float, default=0.0, nullable=False)
    cost_per_lead = Column(Float, default=0.0, nullable=False)
    cost_per_acquisition = Column(Float, default=0.0, nullable=False)
    roi = Column(Float, default=0.0, nullable=False)  # Return on Investment
    
    # Lead metrics
    leads_generated = Column(Integer, default=0, nullable=False)
    leads_qualified = Column(Integer, default=0, nullable=False)
    leads_converted = Column(Integer, default=0, nullable=False)
    
    # Campaign status
    status = Column(String(50), default='active', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_campaign_metrics_org_date', 'organization_id', 'date'),
        Index('idx_campaign_metrics_campaign_date', 'campaign_id', 'date'),
        Index('idx_campaign_metrics_roi', 'organization_id', 'roi'),
    )

class VoiceMetrics(AnalyticsModel):
    """Voice performance metrics model"""
    __tablename__ = "voice_metrics"
    
    voice_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    voice_name = Column(String(255), nullable=False)
    voice_type = Column(String(100), nullable=False)  # male, female, neutral
    voice_language = Column(String(10), nullable=False)  # en-US, es-ES, etc.
    
    # Time dimension
    date = Column(DateTime, nullable=False, index=True)
    
    # Usage metrics
    usage_count = Column(Integer, default=0, nullable=False)
    total_duration = Column(Float, default=0.0, nullable=False)  # seconds
    avg_duration = Column(Float, default=0.0, nullable=False)
    
    # Performance metrics
    success_rate = Column(Float, default=0.0, nullable=False)
    conversion_rate = Column(Float, default=0.0, nullable=False)
    customer_satisfaction = Column(Float, default=0.0, nullable=False)
    
    # Quality metrics
    clarity_score = Column(Float, default=0.0, nullable=False)
    naturalness_score = Column(Float, default=0.0, nullable=False)
    performance_score = Column(Float, default=0.0, nullable=False)
    
    # Cost metrics
    generation_cost = Column(Float, default=0.0, nullable=False)
    cost_per_second = Column(Float, default=0.0, nullable=False)
    total_cost = Column(Float, default=0.0, nullable=False)
    
    # Revenue impact
    revenue_attributed = Column(Float, default=0.0, nullable=False)
    
    __table_args__ = (
        Index('idx_voice_metrics_org_date', 'organization_id', 'date'),
        Index('idx_voice_metrics_voice_date', 'voice_id', 'date'),
        Index('idx_voice_metrics_performance', 'organization_id', 'performance_score'),
    )

class RealTimeMetrics(AnalyticsModel):
    """Real-time metrics snapshot model"""
    __tablename__ = "real_time_metrics"
    
    # Current snapshot data (refreshed every few seconds)
    active_calls = Column(Integer, default=0, nullable=False)
    queued_calls = Column(Integer, default=0, nullable=False)
    available_agents = Column(Integer, default=0, nullable=False)
    busy_agents = Column(Integer, default=0, nullable=False)
    
    # Performance indicators
    avg_wait_time = Column(Float, default=0.0, nullable=False)
    service_level = Column(Float, default=0.0, nullable=False)  # % calls answered within threshold
    abandon_rate = Column(Float, default=0.0, nullable=False)
    
    # System health
    cpu_usage = Column(Float, default=0.0, nullable=False)
    memory_usage = Column(Float, default=0.0, nullable=False)
    api_response_time = Column(Float, default=0.0, nullable=False)
    
    # Revenue tracking
    revenue_today = Column(Float, default=0.0, nullable=False)
    calls_today = Column(Integer, default=0, nullable=False)
    
    # Timestamp for freshness
    snapshot_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_real_time_org_snapshot', 'organization_id', 'snapshot_time'),
    )

class AIInsightsLog(AnalyticsModel):
    """AI insights and recommendations log"""
    __tablename__ = "ai_insights_log"
    
    insight_type = Column(String(100), nullable=False)  # recommendation, prediction, anomaly
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    
    # Insight data
    insight_data = Column(JSON, nullable=True)  # Structured insight data
    confidence_score = Column(Float, default=0.0, nullable=False)
    impact_score = Column(Float, default=0.0, nullable=False)
    
    # Classification
    category = Column(String(100), nullable=False)  # performance, revenue, quality, etc.
    priority = Column(String(20), default='medium', nullable=False)  # low, medium, high, critical
    
    # Status tracking
    status = Column(String(50), default='new', nullable=False)  # new, viewed, applied, dismissed
    applied_at = Column(DateTime, nullable=True)
    applied_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Effectiveness tracking
    outcome = Column(String(100), nullable=True)  # successful, failed, partial
    effectiveness_score = Column(Float, nullable=True)  # How effective was the recommendation
    
    __table_args__ = (
        Index('idx_ai_insights_org_type', 'organization_id', 'insight_type'),
        Index('idx_ai_insights_org_priority', 'organization_id', 'priority'),
        Index('idx_ai_insights_status', 'status', 'created_at'),
    )

class AnalyticsReports(AnalyticsModel):
    """Generated analytics reports model"""
    __tablename__ = "analytics_reports"
    
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False)  # overview, performance, campaign, etc.
    
    # Report configuration
    time_range = Column(String(20), nullable=False)  # 7d, 30d, etc.
    filters = Column(JSON, nullable=True)  # Report filters
    sections = Column(JSON, nullable=False)  # Report sections included
    
    # Generation info
    generated_by = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(50), default='pending', nullable=False)  # pending, generating, completed, failed
    
    # File info
    file_format = Column(String(20), nullable=False)  # pdf, xlsx, csv
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # bytes
    download_url = Column(String(1000), nullable=True)
    
    # Access control
    is_public = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    download_count = Column(Integer, default=0, nullable=False)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        Index('idx_reports_org_type', 'organization_id', 'report_type'),
        Index('idx_reports_status', 'status', 'created_at'),
        Index('idx_reports_expires', 'expires_at'),
    )

class AnalyticsDashboards(AnalyticsModel):
    """Custom analytics dashboards model"""
    __tablename__ = "analytics_dashboards"
    
    dashboard_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Dashboard configuration
    layout = Column(JSON, nullable=False)  # Dashboard layout configuration
    widgets = Column(JSON, nullable=False)  # Widget configurations
    filters = Column(JSON, nullable=True)  # Global dashboard filters
    
    # Access control
    created_by = Column(UUID(as_uuid=True), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Sharing
    shared_with = Column(JSON, nullable=True)  # List of user IDs with access
    share_url = Column(String(500), nullable=True)
    
    # Usage tracking
    view_count = Column(Integer, default=0, nullable=False)
    last_viewed = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_dashboards_org_created', 'organization_id', 'created_by'),
        Index('idx_dashboards_public', 'is_public', 'is_default'),
    )

class AnalyticsCache(Base):
    """Analytics cache storage model"""
    __tablename__ = "analytics_cache"
    
    cache_key = Column(String(255), primary_key=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Cache data
    data = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    # Cache management
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    hit_count = Column(Integer, default=0, nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Data size for management
    data_size = Column(Integer, default=0, nullable=False)  # bytes
    
    __table_args__ = (
        Index('idx_cache_org_expires', 'organization_id', 'expires_at'),
        Index('idx_cache_key_org', 'cache_key', 'organization_id'),
    )

class PerformanceBenchmarks(AnalyticsModel):
    """Performance benchmarks and targets model"""
    __tablename__ = "performance_benchmarks"
    
    benchmark_name = Column(String(255), nullable=False)
    metric_type = Column(String(100), nullable=False)  # success_rate, revenue, satisfaction, etc.
    
    # Benchmark values
    target_value = Column(Float, nullable=False)
    minimum_value = Column(Float, nullable=True)
    maximum_value = Column(Float, nullable=True)
    
    # Context
    industry = Column(String(100), nullable=True)
    campaign_type = Column(String(100), nullable=True)
    agent_level = Column(String(50), nullable=True)  # junior, senior, expert
    
    # Validation
    is_active = Column(Boolean, default=True, nullable=False)
    effective_from = Column(DateTime, default=datetime.utcnow, nullable=False)
    effective_until = Column(DateTime, nullable=True)
    
    # Tracking
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    __table_args__ = (
        Index('idx_benchmarks_org_metric', 'organization_id', 'metric_type'),
        Index('idx_benchmarks_active', 'is_active', 'effective_from'),
    )

class AlertRules(AnalyticsModel):
    """Analytics alert rules configuration"""
    __tablename__ = "alert_rules"
    
    rule_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule configuration
    metric_type = Column(String(100), nullable=False)
    condition = Column(String(50), nullable=False)  # above, below, equals, change
    threshold_value = Column(Float, nullable=False)
    
    # Time window
    time_window = Column(Integer, nullable=False)  # minutes
    evaluation_frequency = Column(Integer, default=5, nullable=False)  # minutes
    
    # Alert settings
    severity = Column(String(20), default='medium', nullable=False)  # low, medium, high, critical
    notification_channels = Column(JSON, nullable=False)  # email, slack, webhook, etc.
    
    # State management
    is_active = Column(Boolean, default=True, nullable=False)
    last_triggered = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0, nullable=False)
    
    # Cooldown to prevent spam
    cooldown_period = Column(Integer, default=30, nullable=False)  # minutes
    
    # Rule ownership
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    __table_args__ = (
        Index('idx_alert_rules_org_active', 'organization_id', 'is_active'),
        Index('idx_alert_rules_metric', 'metric_type', 'is_active'),
    )

class AlertHistory(AnalyticsModel):
    """Alert history and notifications log"""
    __tablename__ = "alert_history"
    
    alert_rule_id = Column(UUID(as_uuid=True), ForeignKey('alert_rules.id'), nullable=False)
    
    # Alert details
    triggered_value = Column(Float, nullable=False)
    threshold_value = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)
    
    # Message content
    alert_title = Column(String(500), nullable=False)
    alert_message = Column(Text, nullable=False)
    
    # Notification status
    notification_status = Column(String(50), default='pending', nullable=False)  # pending, sent, failed
    notification_channels = Column(JSON, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    
    # Resolution
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(UUID(as_uuid=True), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Relationships
    alert_rule = relationship("AlertRules", backref="alert_history")
    
    __table_args__ = (
        Index('idx_alert_history_org_created', 'organization_id', 'created_at'),
        Index('idx_alert_history_rule', 'alert_rule_id', 'created_at'),
        Index('idx_alert_history_status', 'notification_status'),
    )

class DataExports(AnalyticsModel):
    """Data export jobs tracking"""
    __tablename__ = "data_exports"
    
    export_name = Column(String(255), nullable=False)
    export_type = Column(String(100), nullable=False)  # csv, xlsx, pdf, json
    
    # Export configuration
    data_source = Column(String(100), nullable=False)  # calls, agents, campaigns, etc.
    filters = Column(JSON, nullable=True)
    time_range = Column(String(20), nullable=False)
    columns = Column(JSON, nullable=True)  # Specific columns to export
    
    # Job status
    status = Column(String(50), default='pending', nullable=False)  # pending, processing, completed, failed
    progress = Column(Float, default=0.0, nullable=False)  # 0-100
    
    # File details
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # bytes
    row_count = Column(Integer, nullable=True)
    download_url = Column(String(1000), nullable=True)
    
    # Access and expiry
    expires_at = Column(DateTime, nullable=True)
    download_count = Column(Integer, default=0, nullable=False)
    max_downloads = Column(Integer, default=5, nullable=False)
    
    # Job management
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # User tracking
    requested_by = Column(UUID(as_uuid=True), nullable=False)
    
    __table_args__ = (
        Index('idx_exports_org_status', 'organization_id', 'status'),
        Index('idx_exports_user', 'requested_by', 'created_at'),
        Index('idx_exports_expires', 'expires_at'),
    )

class AnalyticsAuditLog(AnalyticsModel):
    """Audit log for analytics operations"""
    __tablename__ = "analytics_audit_log"
    
    # Action details  
    action = Column(String(100), nullable=False)  # view, export, modify, delete
    resource_type = Column(String(100), nullable=False)  # dashboard, report, alert
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    
    # User context
    user_id = Column(UUID(as_uuid=True), nullable=False)
    user_role = Column(String(100), nullable=True)
    
    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Action details
    description = Column(Text, nullable=False)
    old_values = Column(JSON, nullable=True)  # Before values for modifications
    new_values = Column(JSON, nullable=True)  # After values for modifications
    
    # Result
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Additional metadata
    metadata = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('idx_audit_org_action', 'organization_id', 'action'),
        Index('idx_audit_user', 'user_id', 'created_at'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_success', 'success', 'created_at'),
    )

class MetricsAggregation(AnalyticsModel):
    """Pre-aggregated metrics for faster queries"""
    __tablename__ = "metrics_aggregation"
    
    # Aggregation metadata
    metric_name = Column(String(100), nullable=False, index=True)
    aggregation_type = Column(String(20), nullable=False)  # sum, avg, count, min, max
    granularity = Column(String(20), nullable=False)  # hour, day, week, month
    
    # Time dimension
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    
    # Dimensions for grouping
    dimensions = Column(JSON, nullable=True)  # campaign_id, agent_id, voice_id, etc.
    
    # Aggregated values
    value = Column(Float, nullable=False)
    count = Column(Integer, default=0, nullable=False)
    
    # Additional statistics
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    std_deviation = Column(Float, nullable=True)
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
    source_count = Column(Integer, default=0, nullable=False)  # Number of source records
    
    __table_args__ = (
        Index('idx_agg_org_metric_period', 'organization_id', 'metric_name', 'period_start'),
        Index('idx_agg_granularity', 'granularity', 'period_start'),
        Index('idx_agg_updated', 'last_updated'),
    )

# Create all tables function
def create_analytics_tables(engine):
    """Create all analytics tables"""
    Base.metadata.create_all(bind=engine)

# Table cleanup function
def cleanup_old_data(engine, days_to_keep=90):
    """Clean up old analytics data beyond retention period"""
    from sqlalchemy.orm import sessionmaker
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    try:
        # Clean up old cache entries
        session.query(AnalyticsCache).filter(
            AnalyticsCache.expires_at < datetime.utcnow()
        ).delete()
        
        # Clean up old audit logs (keep longer - 1 year)
        audit_cutoff = datetime.utcnow() - timedelta(days=365)
        session.query(AnalyticsAuditLog).filter(
            AnalyticsAuditLog.created_at < audit_cutoff
        ).delete()
        
        # Clean up expired exports
        session.query(DataExports).filter(
            DataExports.expires_at < datetime.utcnow(),
            DataExports.status == 'completed'
        ).delete()
        
        # Clean up old alert history (keep 6 months)
        alert_cutoff = datetime.utcnow() - timedelta(days=180)
        session.query(AlertHistory).filter(
            AlertHistory.created_at < alert_cutoff,
            AlertHistory.resolved_at.isnot(None)
        ).delete()
        
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# Migration scripts
def create_indexes(engine):
    """Create additional performance indexes"""
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # Additional composite indexes for common queries
        conn.execute(text("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_call_metrics_perf_query 
            ON call_metrics (organization_id, date DESC, success_rate DESC);
        """))
        
        conn.execute(text("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_metrics_top_performers 
            ON agent_metrics (organization_id, date DESC, performance_score DESC);
        """))
        
        conn.execute(text("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_campaign_metrics_roi_analysis 
            ON campaign_metrics (organization_id, date DESC, roi DESC);
        """))
        
        conn.execute(text("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_metrics_usage_analysis 
            ON voice_metrics (organization_id, date DESC, usage_count DESC);
        """))
        
        conn.commit()

def create_partitions(engine):
    """Create table partitions for better performance on large datasets"""
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # Partition call_metrics by month
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS call_metrics_y2024m01 
            PARTITION OF call_metrics 
            FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
        """))
        
        # Add more partitions as needed
        conn.commit()

# Model relationships
CallMetrics.agent_metrics = relationship("AgentMetrics", 
                                       foreign_keys=[AgentMetrics.agent_id],
                                       back_populates="call_metrics")

AgentMetrics.call_metrics = relationship("CallMetrics",
                                       foreign_keys=[CallMetrics.agent_id],
                                       back_populates="agent_metrics")

# Export model metadata for migration tools
__all__ = [
    'AnalyticsModel',
    'CallMetrics', 
    'AgentMetrics',
    'CampaignMetrics',
    'VoiceMetrics', 
    'RealTimeMetrics',
    'AIInsightsLog',
    'AnalyticsReports',
    'AnalyticsDashboards',
    'AnalyticsCache',
    'PerformanceBenchmarks',
    'AlertRules',
    'AlertHistory', 
    'DataExports',
    'AnalyticsAuditLog',
    'MetricsAggregation',
    'create_analytics_tables',
    'cleanup_old_data',
    'create_indexes',
    'create_partitions'
]