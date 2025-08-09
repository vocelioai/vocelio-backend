# apps/call-center/src/models/call.py
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class CallStatus(str, enum.Enum):
    QUEUED = "queued"
    RINGING = "ringing" 
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    TRANSFERRED = "transferred"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CallStage(str, enum.Enum):
    OPENING = "opening"
    QUALIFICATION = "qualification"
    PRESENTATION = "presentation"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"
    APPOINTMENT_BOOKING = "appointment_booking"
    PRICING_DISCUSSION = "pricing_discussion"
    INFORMATION_GATHERING = "information_gathering"

class CallPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Call(Base):
    __tablename__ = "calls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Call identification
    twilio_call_sid = Column(String(255), unique=True, nullable=True)
    external_id = Column(String(255), nullable=True)
    
    # Customer information
    customer_phone = Column(String(20), nullable=False)
    customer_name = Column(String(255), nullable=True)
    customer_email = Column(String(255), nullable=True)
    customer_location = Column(String(255), nullable=True)
    customer_type = Column(String(100), nullable=True)  # Lead, Customer, etc.
    customer_age = Column(Integer, nullable=True)
    interest_level = Column(String(50), nullable=True)  # High, Medium, Low
    
    # Call details
    status = Column(Enum(CallStatus), default=CallStatus.QUEUED, nullable=False)
    stage = Column(Enum(CallStage), default=CallStage.OPENING, nullable=True)
    priority = Column(Enum(CallPriority), default=CallPriority.MEDIUM, nullable=False)
    direction = Column(String(20), default="outbound")  # inbound, outbound
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    answered_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Duration in seconds
    duration = Column(Integer, nullable=True)
    ring_duration = Column(Integer, nullable=True)
    talk_duration = Column(Integer, nullable=True)
    
    # Relationships
    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # AI Analysis
    sentiment = Column(String(50), nullable=True)  # positive, neutral, negative, concerned
    confidence_score = Column(Float, nullable=True)
    conversion_probability = Column(Float, nullable=True)
    next_best_action = Column(Text, nullable=True)
    detected_objections = Column(JSONB, nullable=True)
    
    # Call outcome
    outcome = Column(String(100), nullable=True)  # appointment, conversion, no_interest, callback
    outcome_details = Column(JSONB, nullable=True)
    appointment_scheduled = Column(Boolean, default=False)
    appointment_datetime = Column(DateTime, nullable=True)
    
    # Transfer information
    transferred_from_agent_id = Column(UUID(as_uuid=True), nullable=True)
    transferred_to_agent_id = Column(UUID(as_uuid=True), nullable=True)
    transfer_reason = Column(String(255), nullable=True)
    transfer_type = Column(String(50), nullable=True)  # agent, human, queue
    transferred_at = Column(DateTime, nullable=True)
    
    # Recording
    recording_url = Column(String(500), nullable=True)
    recording_sid = Column(String(255), nullable=True)
    recording_status = Column(String(50), nullable=True)
    recording_duration = Column(Integer, nullable=True)
    
    # Compliance
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime, nullable=True)
    dnc_checked = Column(Boolean, default=False)
    compliance_notes = Column(Text, nullable=True)
    
    # Additional metadata
    metadata = Column(JSONB, nullable=True)
    tags = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    agent = relationship("AIAgent", back_populates="calls")
    campaign = relationship("Campaign", back_populates="calls")
    conversations = relationship("Conversation", back_populates="call", cascade="all, delete-orphan")
    recordings = relationship("CallRecording", back_populates="call", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Call {self.id} - {self.customer_phone} - {self.status}>"

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"), nullable=False)
    
    # Message details
    speaker = Column(String(20), nullable=False)  # agent, customer, system
    message = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, action, system
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    timestamp_in_call = Column(Float, nullable=True)  # Seconds from call start
    
    # AI Analysis
    sentiment = Column(String(50), nullable=True)
    intent = Column(String(100), nullable=True)
    entities = Column(JSONB, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Audio information (if applicable)
    audio_url = Column(String(500), nullable=True)
    audio_duration = Column(Float, nullable=True)
    transcription_confidence = Column(Float, nullable=True)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    call = relationship("Call", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation {self.id} - {self.speaker}: {self.message[:50]}...>"

class CallRecording(Base):
    __tablename__ = "call_recordings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"), nullable=False)
    
    # Recording details
    twilio_recording_sid = Column(String(255), nullable=True)
    recording_url = Column(String(500), nullable=False)
    recording_status = Column(String(50), nullable=False)  # in-progress, completed, failed
    
    # Timing
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # seconds
    
    # File information
    file_size = Column(Integer, nullable=True)  # bytes
    file_format = Column(String(20), nullable=True)  # mp3, wav, etc.
    quality = Column(String(20), nullable=True)  # high, medium, low
    
    # Processing
    transcription_status = Column(String(50), nullable=True)  # pending, completed, failed
    transcription_url = Column(String(500), nullable=True)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Compliance
    consent_recorded = Column(Boolean, default=False)
    retention_policy = Column(String(100), nullable=True)
    deletion_scheduled_at = Column(DateTime, nullable=True)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    call = relationship("Call", back_populates="recordings")
    
    def __repr__(self):
        return f"<CallRecording {self.id} - {self.call_id} - {self.recording_status}>"

# AI Agent model (referenced in Call)
class AIAgent(Base):
    __tablename__ = "ai_agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255), nullable=True)
    voice_id = Column(String(255), nullable=False)
    language = Column(String(10), default="en-US")
    
    # Performance metrics
    performance_score = Column(Float, default=0.0)
    total_calls = Column(Integer, default=0)
    successful_calls = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    
    # Configuration
    personality_traits = Column(JSONB, nullable=True)
    optimization_status = Column(String(50), default="active")
    last_optimized = Column(DateTime, nullable=True)
    status = Column(String(50), default="active")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    calls = relationship("Call", back_populates="agent")

# Campaign model (referenced in Call)
class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=True)
    type = Column(String(100), nullable=True)  # cold_call, follow_up, appointment_setting
    
    # Campaign configuration
    priority = Column(Enum(CallPriority), default=CallPriority.MEDIUM)
    target_audience = Column(JSONB, nullable=True)
    script_template = Column(Text, nullable=True)
    
    # Status and metrics
    status = Column(String(50), default="active")
    total_calls = Column(Integer, default=0)
    successful_calls = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    
    # Timing
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    calls = relationship("Call", back_populates="campaign")