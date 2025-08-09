# apps/smart-campaigns/src/models/campaign.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

from shared.database.models import BaseModel
from core.config import CampaignStatus, CampaignPriority, CampaignType

Base = declarative_base()

class Campaign(BaseModel):
    __tablename__ = "campaigns"
    
    # Basic Information
    id = Column(String, primary_key=True, default=lambda: f"camp_{uuid.uuid4().hex[:12]}")
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    industry = Column(String(100), index=True)
    campaign_type = Column(String(50), default=CampaignType.OUTBOUND_CALL, index=True)
    
    # Status & Priority
    status = Column(String(20), default=CampaignStatus.DRAFT, index=True)
    priority = Column(String(20), default=CampaignPriority.MEDIUM, index=True)
    
    # Owner & Organization
    user_id = Column(String, nullable=False, index=True)
    organization_id = Column(String, nullable=False, index=True)
    
    # Agent Configuration
    agent_id = Column(String, nullable=False, index=True)
    agent_name = Column(String(255))
    voice_id = Column(String)
    
    # Campaign Settings
    settings = Column(JSON, default={})
    
    # Location & Targeting
    location = Column(String(255))
    target_demographics = Column(JSON, default={})
    
    # Scheduling
    schedule_config = Column(JSON, default={})
    start_time = Column(String(10))  # "9:00 AM"
    end_time = Column(String(10))    # "6:00 PM"
    timezone = Column(String(50), default="UTC")
    
    # Performance Metrics
    total_prospects = Column(Integer, default=0)
    calls_made = Column(Integer, default=0)
    calls_answered = Column(Integer, default=0)
    calls_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    average_call_duration = Column(Float, default=0.0)
    
    # Financial Metrics
    total_cost = Column(Float, default=0.0)
    revenue_generated = Column(Float, default=0.0)
    cost_per_lead = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    
    # Progress Tracking
    progress_percentage = Column(Float, default=0.0)
    
    # AI & Optimization
    ai_optimization_enabled = Column(Boolean, default=True)
    ai_optimization_score = Column(Float, default=0.0)
    optimization_suggestions = Column(JSON, default=[])
    
    # A/B Testing
    is_ab_test = Column(Boolean, default=False)
    ab_test_config = Column(JSON, default={})
    ab_test_results = Column(JSON, default={})
    
    # Predictions
    predicted_success_rate = Column(Float)
    predicted_revenue = Column(Float)
    prediction_confidence = Column(Float)
    
    # Live Metrics (for active campaigns)
    live_calls = Column(Integer, default=0)
    calls_today = Column(Integer, default=0)
    conversions_today = Column(Integer, default=0)
    
    # Tags & Classification
    tags = Column(JSON, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    last_activity_at = Column(DateTime(timezone=True))
    
    # Relationships
    prospects = relationship("Prospect", back_populates="campaign", cascade="all, delete-orphan")
    schedules = relationship("CampaignSchedule", back_populates="campaign", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_campaign_user_status', 'user_id', 'status'),
        Index('idx_campaign_org_industry', 'organization_id', 'industry'),
        Index('idx_campaign_agent_status', 'agent_id', 'status'),
        Index('idx_campaign_created_at', 'created_at'),
        Index('idx_campaign_last_activity', 'last_activity_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'industry': self.industry,
            'campaign_type': self.campaign_type,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'organization_id': self.organization_id,
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'voice_id': self.voice_id,
            'settings': self.settings,
            'location': self.location,
            'target_demographics': self.target_demographics,
            'schedule_config': self.schedule_config,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'timezone': self.timezone,
            'total_prospects': self.total_prospects,
            'calls_made': self.calls_made,
            'calls_answered': self.calls_answered,
            'calls_completed': self.calls_completed,
            'success_rate': self.success_rate,
            'conversion_rate': self.conversion_rate,
            'average_call_duration': self.average_call_duration,
            'total_cost': self.total_cost,
            'revenue_generated': self.revenue_generated,
            'cost_per_lead': self.cost_per_lead,
            'roi': self.roi,
            'progress_percentage': self.progress_percentage,
            'ai_optimization_enabled': self.ai_optimization_enabled,
            'ai_optimization_score': self.ai_optimization_score,
            'optimization_suggestions': self.optimization_suggestions,
            'is_ab_test': self.is_ab_test,
            'ab_test_config': self.ab_test_config,
            'ab_test_results': self.ab_test_results,
            'predicted_success_rate': self.predicted_success_rate,
            'predicted_revenue': self.predicted_revenue,
            'prediction_confidence': self.prediction_confidence,
            'live_calls': self.live_calls,
            'calls_today': self.calls_today,
            'conversions_today': self.conversions_today,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
        }
    
    @property
    def is_active(self) -> bool:
        """Check if campaign is currently active"""
        return self.status in [CampaignStatus.ACTIVE, CampaignStatus.RUNNING]
    
    @property
    def can_be_started(self) -> bool:
        """Check if campaign can be started"""
        return self.status in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED, CampaignStatus.PAUSED]
    
    @property
    def can_be_paused(self) -> bool:
        """Check if campaign can be paused"""
        return self.status in [CampaignStatus.ACTIVE, CampaignStatus.RUNNING]
    
    def calculate_success_rate(self) -> float:
        """Calculate current success rate"""
        if self.calls_made == 0:
            return 0.0
        return (self.calls_completed / self.calls_made) * 100
    
    def calculate_conversion_rate(self) -> float:
        """Calculate conversion rate"""
        if self.calls_answered == 0:
            return 0.0
        return (self.calls_completed / self.calls_answered) * 100
    
    def update_live_metrics(self, live_calls: int, calls_today: int, conversions_today: int):
        """Update live metrics"""
        self.live_calls = live_calls
        self.calls_today = calls_today
        self.conversions_today = conversions_today
        self.last_activity_at = func.now()


# Campaign Schedule Model
class CampaignSchedule(BaseModel):
    __tablename__ = "campaign_schedules"
    
    id = Column(String, primary_key=True, default=lambda: f"sched_{uuid.uuid4().hex[:12]}")
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Schedule Configuration
    schedule_type = Column(String(20), default="immediate")  # immediate, scheduled, recurring
    scheduled_start = Column(DateTime(timezone=True))
    scheduled_end = Column(DateTime(timezone=True))
    
    # Recurring Configuration
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSON, default={})  # daily, weekly, monthly patterns
    
    # Time Windows
    daily_start_time = Column(String(10))  # "09:00"
    daily_end_time = Column(String(10))    # "17:00"
    timezone = Column(String(50), default="UTC")
    
    # Days of Week (0 = Monday, 6 = Sunday)
    allowed_days = Column(JSON, default=[0, 1, 2, 3, 4])  # Weekdays by default
    
    # Execution Status
    status = Column(String(20), default="pending")
    last_executed = Column(DateTime(timezone=True))
    next_execution = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="schedules")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'schedule_type': self.schedule_type,
            'scheduled_start': self.scheduled_start.isoformat() if self.scheduled_start else None,
            'scheduled_end': self.scheduled_end.isoformat() if self.scheduled_end else None,
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern,
            'daily_start_time': self.daily_start_time,
            'daily_end_time': self.daily_end_time,
            'timezone': self.timezone,
            'allowed_days': self.allowed_days,
            'status': self.status,
            'last_executed': self.last_executed.isoformat() if self.last_executed else None,
            'next_execution': self.next_execution.isoformat() if self.next_execution else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }