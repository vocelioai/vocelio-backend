# apps/smart-campaigns/src/models/enhanced_campaign.py
"""
Enhanced Campaign Models - Merged from smart-campaigns + smart-campaigns-service
Combines structured campaign management with AI optimization features
"""

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

class EnhancedCampaign(BaseModel):
    """Enhanced Campaign model with AI optimization features"""
    __tablename__ = "enhanced_campaigns"
    
    # Basic Information (from smart-campaigns)
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
    ai_agent_ids = Column(JSON, default=list)  # Multiple AI agents support
    
    # Campaign Settings
    settings = Column(JSON, default={})
    
    # Location & Targeting
    location = Column(String(255))
    target_demographics = Column(JSON, default={})
    target_audience_size = Column(Integer, default=0)
    
    # Scheduling
    schedule_config = Column(JSON, default={})
    start_time = Column(String(10))
    end_time = Column(String(10))
    timezone = Column(String(50), default="UTC")
    
    # AI Optimization Features (from smart-campaigns-service)
    optimization_goal = Column(String(50), default="maximize_revenue")
    is_ai_optimized = Column(Boolean, default=False)
    optimization_history = Column(JSON, default=list)
    
    # Performance Metrics (from smart-campaigns-service)
    total_calls = Column(Integer, default=0)
    successful_calls = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    revenue_generated = Column(Float, default=0.0)
    cost_per_acquisition = Column(Float, default=0.0)
    roi_percentage = Column(Float, default=0.0)
    
    # Campaign Limits
    daily_call_limit = Column(Integer, default=1000)
    max_prospects = Column(Integer, default=10000)
    
    # Script and Templates
    script_template = Column(Text, default="")
    template_id = Column(String)  # Reference to campaign template
    
    # A/B Testing Support
    is_ab_test = Column(Boolean, default=False)
    ab_test_config = Column(JSON, default={})
    parent_campaign_id = Column(String, ForeignKey('enhanced_campaigns.id'))
    
    # Analytics and Tracking
    analytics_data = Column(JSON, default={})
    performance_metrics = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    parent_campaign = relationship("EnhancedCampaign", remote_side=[id])
    child_campaigns = relationship("EnhancedCampaign", back_populates="parent_campaign")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_campaign_status_org', 'status', 'organization_id'),
        Index('idx_campaign_user_type', 'user_id', 'campaign_type'),
        Index('idx_campaign_industry_status', 'industry', 'status'),
        Index('idx_campaign_created_at', 'created_at'),
        Index('idx_campaign_ai_optimized', 'is_ai_optimized'),
    )

class CampaignTemplate(BaseModel):
    """Campaign templates for quick campaign creation"""
    __tablename__ = "campaign_templates"
    
    id = Column(String, primary_key=True, default=lambda: f"tmpl_{uuid.uuid4().hex[:12]}")
    name = Column(String(255), nullable=False)
    description = Column(Text)
    industry = Column(String(100), index=True)
    campaign_type = Column(String(50), index=True)
    
    # Template configuration
    template_config = Column(JSON, default={})
    script_template = Column(Text)
    recommended_settings = Column(JSON, default={})
    
    # Performance benchmarks
    avg_conversion_rate = Column(Float, default=0.0)
    avg_roi = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    
    # Metadata
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(String)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class CampaignOptimization(BaseModel):
    """Track AI optimization experiments and results"""
    __tablename__ = "campaign_optimizations"
    
    id = Column(String, primary_key=True, default=lambda: f"opt_{uuid.uuid4().hex[:12]}")
    campaign_id = Column(String, ForeignKey('enhanced_campaigns.id'), nullable=False)
    
    # Optimization details
    optimization_type = Column(String(50), nullable=False)  # "script", "timing", "targeting"
    optimization_goal = Column(String(50), nullable=False)
    
    # Before/After metrics
    metrics_before = Column(JSON, default={})
    metrics_after = Column(JSON, default={})
    improvement_percentage = Column(Float, default=0.0)
    
    # Optimization configuration
    changes_made = Column(JSON, default={})
    ai_recommendations = Column(JSON, default={})
    
    # Status and timing
    status = Column(String(20), default="running")  # running, completed, failed
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    # Results
    is_successful = Column(Boolean)
    confidence_score = Column(Float, default=0.0)
    
    campaign = relationship("EnhancedCampaign", back_populates="optimizations")

# Add the optimization relationship to EnhancedCampaign
EnhancedCampaign.optimizations = relationship("CampaignOptimization", back_populates="campaign")

class ABTest(BaseModel):
    """A/B testing for campaign optimization"""
    __tablename__ = "ab_tests"
    
    id = Column(String, primary_key=True, default=lambda: f"ab_{uuid.uuid4().hex[:12]}")
    campaign_id = Column(String, ForeignKey('enhanced_campaigns.id'), nullable=False)
    
    # Test configuration
    test_name = Column(String(255), nullable=False)
    test_type = Column(String(50), nullable=False)  # "script", "voice", "timing"
    variant_a_config = Column(JSON, default={})
    variant_b_config = Column(JSON, default={})
    
    # Test parameters
    traffic_split = Column(Float, default=50.0)  # Percentage for variant A
    minimum_sample_size = Column(Integer, default=100)
    confidence_level = Column(Float, default=95.0)
    
    # Results
    variant_a_metrics = Column(JSON, default={})
    variant_b_metrics = Column(JSON, default={})
    winner = Column(String(10))  # "A", "B", or "inconclusive"
    statistical_significance = Column(Float, default=0.0)
    
    # Status and timing
    status = Column(String(20), default="setup")  # setup, running, completed, stopped
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    
    created_at = Column(DateTime, default=func.now())
    
    campaign = relationship("EnhancedCampaign")
