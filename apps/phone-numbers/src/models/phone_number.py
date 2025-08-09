# apps/phone-numbers/src/models/phone_number.py
from sqlalchemy import Column, String, DateTime, Boolean, Float, Integer, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

Base = declarative_base()


class PhoneNumber(Base):
    """Phone Number Model"""
    __tablename__ = "phone_numbers"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    twilio_sid = Column(String, unique=True, nullable=False, index=True)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    friendly_name = Column(String, nullable=False)
    
    # Organization/User association
    organization_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Geographic information
    country_code = Column(String(2), nullable=False, index=True)
    region = Column(String, nullable=True)  # State/Province
    locality = Column(String, nullable=True)  # City
    postal_code = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Number classification
    number_type = Column(String, nullable=False, index=True)  # local, toll_free, mobile
    capabilities = Column(JSON, nullable=False)  # ["voice", "sms", "mms"]
    
    # Twilio configuration
    voice_url = Column(String, nullable=True)
    voice_method = Column(String, default="POST")
    voice_fallback_url = Column(String, nullable=True)
    voice_fallback_method = Column(String, default="POST")
    
    sms_url = Column(String, nullable=True) 
    sms_method = Column(String, default="POST")
    sms_fallback_url = Column(String, nullable=True)
    sms_fallback_method = Column(String, default="POST")
    
    status_callback = Column(String, nullable=True)
    status_callback_method = Column(String, default="POST")
    
    # Status and configuration
    status = Column(String, default="active", index=True)  # active, inactive, released
    emergency_enabled = Column(Boolean, default=False)
    emergency_address_sid = Column(String, nullable=True)
    
    # Billing information
    monthly_price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    billing_cycle_day = Column(Integer, default=1)
    
    # Usage tracking
    total_calls = Column(Integer, default=0)
    total_minutes = Column(Float, default=0.0)
    total_sms = Column(Integer, default=0)
    total_mms = Column(Integer, default=0)
    
    # Campaign associations
    campaign_count = Column(Integer, default=0)
    active_campaign_count = Column(Integer, default=0)
    
    # Metadata
    tags = Column(JSON, nullable=True)  # User-defined tags
    notes = Column(Text, nullable=True)
    custom_properties = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    purchased_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    released_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<PhoneNumber(id={self.id}, number={self.phone_number}, type={self.number_type})>"
    
    @property
    def formatted_number(self) -> str:
        """Return formatted phone number"""
        if self.country_code == "US" or self.country_code == "CA":
            # Format as +1 (555) 123-4567
            clean = self.phone_number.replace("+", "").replace("-", "").replace("(", "").replace(")", "").replace(" ", "")
            if len(clean) == 11 and clean.startswith("1"):
                area = clean[1:4]
                exchange = clean[4:7] 
                number = clean[7:11]
                return f"+1 ({area}) {exchange}-{number}"
        return self.phone_number
    
    @property
    def usage_summary(self) -> Dict[str, Any]:
        """Return usage summary"""
        return {
            "calls": self.total_calls,
            "minutes": round(self.total_minutes, 2),
            "sms": self.total_sms,
            "mms": self.total_mms
        }


class PhoneNumberVerification(Base):
    """Phone Number Verification Model"""
    __tablename__ = "phone_number_verifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number_id = Column(String, ForeignKey("phone_numbers.id"), nullable=False)
    
    # Verification details
    verification_type = Column(String, nullable=False)  # ownership, compliance, carrier
    status = Column(String, default="pending")  # pending, verified, failed
    verification_code = Column(String, nullable=True)
    verification_method = Column(String, nullable=True)  # sms, voice, email
    
    # Results
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    requested_by = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    phone_number = relationship("PhoneNumber", backref="verifications")


class PhoneNumberPurchase(Base):
    """Phone Number Purchase Transaction Model"""
    __tablename__ = "phone_number_purchases"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number_id = Column(String, ForeignKey("phone_numbers.id"), nullable=False)
    
    # Purchase details
    organization_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Pricing information
    base_price = Column(Float, nullable=False)
    setup_fee = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Payment information
    stripe_payment_intent_id = Column(String, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    payment_status = Column(String, default="pending")  # pending, succeeded, failed
    payment_method = Column(String, nullable=True)
    
    # Twilio information
    twilio_purchase_data = Column(JSON, nullable=True)
    provisioning_status = Column(String, default="pending")  # pending, provisioned, failed
    provisioning_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    payment_completed_at = Column(DateTime(timezone=True), nullable=True)
    provisioned_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    phone_number = relationship("PhoneNumber", backref="purchase_history")


class PhoneNumberUsage(Base):
    """Phone Number Usage Tracking Model"""
    __tablename__ = "phone_number_usage"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number_id = Column(String, ForeignKey("phone_numbers.id"), nullable=False)
    
    # Usage period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Call usage
    inbound_calls = Column(Integer, default=0)
    outbound_calls = Column(Integer, default=0)
    total_call_duration = Column(Float, default=0.0)  # in minutes
    
    # Messaging usage
    inbound_sms = Column(Integer, default=0)
    outbound_sms = Column(Integer, default=0)
    inbound_mms = Column(Integer, default=0)
    outbound_mms = Column(Integer, default=0)
    
    # Cost tracking
    call_costs = Column(Float, default=0.0)
    sms_costs = Column(Float, default=0.0)
    mms_costs = Column(Float, default=0.0)
    total_costs = Column(Float, default=0.0)
    
    # Campaign tracking
    campaign_id = Column(String, nullable=True, index=True)
    campaign_name = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    phone_number = relationship("PhoneNumber", backref="usage_records")


class NumberPorting(Base):
    """Number Porting Request Model"""
    __tablename__ = "number_porting"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number_id = Column(String, ForeignKey("phone_numbers.id"), nullable=True)
    
    # Porting details
    organization_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    external_phone_number = Column(String, nullable=False)
    current_carrier = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    pin_code = Column(String, nullable=True)
    
    # Porting status
    status = Column(String, default="submitted")  # submitted, pending, approved, completed, failed
    twilio_porting_sid = Column(String, nullable=True)
    
    # Documentation
    documentation_url = Column(String, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship (nullable because number might not exist yet)
    phone_number = relationship("PhoneNumber", backref="porting_requests")


# Additional indexes for performance
from sqlalchemy import Index

# Composite indexes for common queries
Index('idx_phone_numbers_org_status', PhoneNumber.organization_id, PhoneNumber.status)
Index('idx_phone_numbers_country_type', PhoneNumber.country_code, PhoneNumber.number_type)
Index('idx_usage_number_period', PhoneNumberUsage.phone_number_id, PhoneNumberUsage.period_start)
Index('idx_purchases_org_status', PhoneNumberPurchase.organization_id, PhoneNumberPurchase.payment_status)