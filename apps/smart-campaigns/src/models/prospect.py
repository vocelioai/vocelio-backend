# apps/smart-campaigns/src/models/prospect.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

from shared.database.models import BaseModel
from core.config import ProspectStatus

class Prospect(BaseModel):
    __tablename__ = "prospects"
    
    # Basic Information
    id = Column(String, primary_key=True, default=lambda: f"prospect_{uuid.uuid4().hex[:12]}")
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Contact Information
    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(255), index=True)
    email = Column(String(255), index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    
    # Additional Contact Details
    company = Column(String(255))
    job_title = Column(String(255))
    industry = Column(String(100))
    
    # Address Information
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(50), default="US")
    
    # Status & Classification
    status = Column(String(30), default=ProspectStatus.NEW, index=True)
    priority = Column(String(20), default="medium")
    lead_score = Column(Float, default=0.0)
    
    # Custom Data
    custom_fields = Column(JSON, default={})
    tags = Column(JSON, default=[])
    notes = Column(Text)
    
    # Call History Tracking
    total_calls = Column(Integer, default=0)
    successful_calls = Column(Integer, default=0)
    failed_calls = Column(Integer, default=0)
    no_answer_count = Column(Integer, default=0)
    busy_count = Column(Integer, default=0)
    voicemail_count = Column(Integer, default=0)
    
    # Last Call Information
    last_call_id = Column(String)
    last_call_date = Column(DateTime(timezone=True))
    last_call_status = Column(String(30))
    last_call_duration = Column(Float)  # in seconds
    last_call_outcome = Column(String(50))
    
    # Conversion Tracking
    is_converted = Column(Boolean, default=False)
    conversion_date = Column(DateTime(timezone=True))
    conversion_value = Column(Float)
    conversion_type = Column(String(50))
    
    # Scheduling
    next_call_scheduled = Column(DateTime(timezone=True))
    best_time_to_call = Column(String(50))  # "morning", "afternoon", "evening"
    timezone = Column(String(50))
    do_not_call_before = Column(DateTime(timezone=True))
    
    # AI & Predictions
    ai_prediction_score = Column(Float)  # Likelihood of success
    predicted_outcome = Column(String(50))
    optimal_call_time = Column(String(10))  # "14:30"
    
    # Compliance
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime(timezone=True))
    opt_out_requested = Column(Boolean, default=False)
    opt_out_date = Column(DateTime(timezone=True))
    dnc_listed = Column(Boolean, default=False)
    
    # Source Information
    source = Column(String(100))  # "upload", "api", "import", "manual"
    source_campaign = Column(String(255))
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))
    
    # Engagement Metrics
    email_opens = Column(Integer, default=0)
    email_clicks = Column(Integer, default=0)
    website_visits = Column(Integer, default=0)
    last_engagement_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    first_contacted_at = Column(DateTime(timezone=True))
    
    # Relationships
    campaign = relationship("Campaign", back_populates="prospects")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_prospect_campaign_status', 'campaign_id', 'status'),
        Index('idx_prospect_phone_campaign', 'phone_number', 'campaign_id'),
        Index('idx_prospect_email_campaign', 'email', 'campaign_id'),
        Index('idx_prospect_next_call', 'next_call_scheduled'),
        Index('idx_prospect_last_call', 'last_call_date'),
        Index('idx_prospect_conversion', 'is_converted', 'conversion_date'),
        Index('idx_prospect_dnc', 'dnc_listed', 'opt_out_requested'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'company': self.company,
            'job_title': self.job_title,
            'industry': self.industry,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'status': self.status,
            'priority': self.priority,
            'lead_score': self.lead_score,
            'custom_fields': self.custom_fields,
            'tags': self.tags,
            'notes': self.notes,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'no_answer_count': self.no_answer_count,
            'busy_count': self.busy_count,
            'voicemail_count': self.voicemail_count,
            'last_call_id': self.last_call_id,
            'last_call_date': self.last_call_date.isoformat() if self.last_call_date else None,
            'last_call_status': self.last_call_status,
            'last_call_duration': self.last_call_duration,
            'last_call_outcome': self.last_call_outcome,
            'is_converted': self.is_converted,
            'conversion_date': self.conversion_date.isoformat() if self.conversion_date else None,
            'conversion_value': self.conversion_value,
            'conversion_type': self.conversion_type,
            'next_call_scheduled': self.next_call_scheduled.isoformat() if self.next_call_scheduled else None,
            'best_time_to_call': self.best_time_to_call,
            'timezone': self.timezone,
            'do_not_call_before': self.do_not_call_before.isoformat() if self.do_not_call_before else None,
            'ai_prediction_score': self.ai_prediction_score,
            'predicted_outcome': self.predicted_outcome,
            'optimal_call_time': self.optimal_call_time,
            'consent_given': self.consent_given,
            'consent_date': self.consent_date.isoformat() if self.consent_date else None,
            'opt_out_requested': self.opt_out_requested,
            'opt_out_date': self.opt_out_date.isoformat() if self.opt_out_date else None,
            'dnc_listed': self.dnc_listed,
            'source': self.source,
            'source_campaign': self.source_campaign,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'email_opens': self.email_opens,
            'email_clicks': self.email_clicks,
            'website_visits': self.website_visits,
            'last_engagement_date': self.last_engagement_date.isoformat() if self.last_engagement_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'first_contacted_at': self.first_contacted_at.isoformat() if self.first_contacted_at else None,
        }
    
    @property
    def success_rate(self) -> float:
        """Calculate individual prospect success rate"""
        if self.total_calls == 0:
            return 0.0
        return (self.successful_calls / self.total_calls) * 100
    
    @property
    def answer_rate(self) -> float:
        """Calculate answer rate for this prospect"""
        if self.total_calls == 0:
            return 0.0
        answered_calls = self.total_calls - self.no_answer_count - self.busy_count
        return (answered_calls / self.total_calls) * 100
    
    @property
    def can_be_called(self) -> bool:
        """Check if prospect can be called"""
        if self.dnc_listed or self.opt_out_requested:
            return False
        if self.do_not_call_before and datetime.utcnow() < self.do_not_call_before:
            return False
        return True
    
    def update_call_stats(self, call_status: str, duration: float = 0, outcome: str = None):
        """Update call statistics"""
        self.total_calls += 1
        self.last_call_date = func.now()
        self.last_call_status = call_status
        self.last_call_duration = duration
        self.last_call_outcome = outcome
        
        if call_status == ProspectStatus.ANSWERED:
            self.successful_calls += 1
        elif call_status == ProspectStatus.NO_ANSWER:
            self.no_answer_count += 1
            self.failed_calls += 1
        elif call_status == ProspectStatus.BUSY:
            self.busy_count += 1
            self.failed_calls += 1
        elif call_status == ProspectStatus.VOICEMAIL:
            self.voicemail_count += 1
        else:
            self.failed_calls += 1
    
    def mark_converted(self, conversion_value: float = None, conversion_type: str = None):
        """Mark prospect as converted"""
        self.is_converted = True
        self.conversion_date = func.now()
        self.status = ProspectStatus.CONVERTED
        if conversion_value:
            self.conversion_value = conversion_value
        if conversion_type:
            self.conversion_type = conversion_type
    
    def opt_out(self):
        """Mark prospect as opted out"""
        self.opt_out_requested = True
        self.opt_out_date = func.now()
        self.status = ProspectStatus.DO_NOT_CALL