"""
Phone System Schema Definitions for Call Center
Comprehensive data models for phone number and extension management
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class PhoneNumberStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ASSIGNED = "assigned"
    AVAILABLE = "available"


class PhoneNumberType(str, Enum):
    LOCAL = "local"
    TOLL_FREE = "toll_free"
    INTERNATIONAL = "international"
    VIRTUAL = "virtual"


class ExtensionType(str, Enum):
    AGENT = "agent"
    DEPARTMENT = "department"
    CONFERENCE = "conference"
    VOICEMAIL = "voicemail"
    IVR = "ivr"


class PhoneNumberBase(BaseModel):
    number: str = Field(..., description="Phone number in E.164 format")
    display_name: str = Field(..., description="Display name for the number")
    type: PhoneNumberType = Field(..., description="Type of phone number")
    country_code: str = Field(..., description="Country code (e.g., 'US', 'CA')")
    area_code: Optional[str] = Field(None, description="Area code")
    is_toll_free: bool = Field(False, description="Whether number is toll-free")
    monthly_cost: float = Field(0.0, description="Monthly cost in USD")


class PhoneNumberCreate(PhoneNumberBase):
    auto_assign: bool = Field(False, description="Auto-assign to available agent")


class PhoneNumberUpdate(BaseModel):
    display_name: Optional[str] = None
    status: Optional[PhoneNumberStatus] = None
    assigned_to: Optional[str] = None
    routing_config: Optional[Dict[str, Any]] = None


class PhoneNumber(PhoneNumberBase):
    id: str = Field(..., description="Unique identifier")
    status: PhoneNumberStatus = Field(..., description="Current status")
    assigned_to: Optional[str] = Field(None, description="Assigned agent/department ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    routing_config: Dict[str, Any] = Field(default_factory=dict, description="Routing configuration")
    usage_stats: Dict[str, Any] = Field(default_factory=dict, description="Usage statistics")

    class Config:
        from_attributes = True


class ExtensionBase(BaseModel):
    extension: str = Field(..., description="Extension number")
    display_name: str = Field(..., description="Display name")
    type: ExtensionType = Field(..., description="Extension type")
    phone_number_id: Optional[str] = Field(None, description="Associated phone number ID")


class ExtensionCreate(ExtensionBase):
    auto_configure: bool = Field(True, description="Auto-configure based on type")


class ExtensionUpdate(BaseModel):
    display_name: Optional[str] = None
    status: Optional[PhoneNumberStatus] = None
    phone_number_id: Optional[str] = None
    routing_rules: Optional[Dict[str, Any]] = None


class Extension(ExtensionBase):
    id: str = Field(..., description="Unique identifier")
    status: PhoneNumberStatus = Field(..., description="Current status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    routing_rules: Dict[str, Any] = Field(default_factory=dict, description="Routing rules")
    assigned_agent: Optional[str] = Field(None, description="Assigned agent ID")

    class Config:
        from_attributes = True


class PhoneSystemStatus(BaseModel):
    total_numbers: int = Field(..., description="Total phone numbers")
    active_numbers: int = Field(..., description="Active numbers")
    available_numbers: int = Field(..., description="Available numbers")
    total_extensions: int = Field(..., description="Total extensions")
    active_extensions: int = Field(..., description="Active extensions")
    system_health: str = Field(..., description="Overall system health")
    provider_status: Dict[str, str] = Field(default_factory=dict, description="Provider status")
    last_updated: datetime = Field(..., description="Last status update")


class CapacityMetrics(BaseModel):
    concurrent_calls_limit: int = Field(..., description="Maximum concurrent calls")
    current_active_calls: int = Field(..., description="Current active calls")
    utilization_percentage: float = Field(..., description="Current utilization %")
    peak_calls_today: int = Field(..., description="Peak calls today")
    peak_time: Optional[datetime] = Field(None, description="Peak time today")
    bandwidth_usage: Dict[str, float] = Field(default_factory=dict, description="Bandwidth metrics")


class PhoneTestRequest(BaseModel):
    test_type: str = Field(..., description="Type of test (connectivity, quality, etc.)")
    duration: int = Field(60, description="Test duration in seconds")
    target_number: Optional[str] = Field(None, description="Target number for test call")


class PhoneTestResult(BaseModel):
    test_id: str = Field(..., description="Test identifier")
    phone_number_id: str = Field(..., description="Tested phone number ID")
    test_type: str = Field(..., description="Type of test performed")
    status: str = Field(..., description="Test result status")
    quality_score: float = Field(..., description="Quality score (0-100)")
    latency_ms: float = Field(..., description="Average latency in milliseconds")
    packet_loss: float = Field(..., description="Packet loss percentage")
    jitter_ms: float = Field(..., description="Jitter in milliseconds")
    started_at: datetime = Field(..., description="Test start time")
    completed_at: datetime = Field(..., description="Test completion time")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed test results")


class NumberAssignmentRequest(BaseModel):
    phone_number_id: str = Field(..., description="Phone number to assign")
    assign_to: str = Field(..., description="Agent or department ID")
    assignment_type: str = Field(..., description="Type: 'agent' or 'department'")
    priority: int = Field(1, description="Assignment priority (1-10)")
    effective_date: Optional[datetime] = Field(None, description="When assignment takes effect")


class NumberAssignmentResponse(BaseModel):
    assignment_id: str = Field(..., description="Assignment identifier")
    phone_number_id: str = Field(..., description="Assigned phone number ID")
    assigned_to: str = Field(..., description="Assigned to ID")
    assignment_type: str = Field(..., description="Assignment type")
    status: str = Field(..., description="Assignment status")
    created_at: datetime = Field(..., description="Assignment creation time")
    effective_at: datetime = Field(..., description="When assignment becomes effective")


class PhoneNumberListResponse(BaseModel):
    numbers: List[PhoneNumber] = Field(..., description="List of phone numbers")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    has_more: bool = Field(..., description="More results available")


class ExtensionListResponse(BaseModel):
    extensions: List[Extension] = Field(..., description="List of extensions")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    has_more: bool = Field(..., description="More results available")
