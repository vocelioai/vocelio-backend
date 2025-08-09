"""
Organization Settings Schemas
Pydantic models for organization settings requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class BusinessHours(BaseModel):
    """Business hours configuration"""
    start: str = Field(..., description="Start time in HH:MM format")
    end: str = Field(..., description="End time in HH:MM format")
    timezone: str = Field(..., description="Timezone identifier")
    workdays: List[str] = Field(..., description="List of working days")
    
    @validator('start', 'end')
    def validate_time_format(cls, v):
        """Validate time format HH:MM"""
        try:
            hour, minute = map(int, v.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError('Invalid time format')
            return v
        except (ValueError, AttributeError):
            raise ValueError('Time must be in HH:MM format')
    
    @validator('workdays')
    def validate_workdays(cls, v):
        """Validate workdays list"""
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in v:
            if day.lower() not in valid_days:
                raise ValueError(f'Invalid workday: {day}')
        return [day.lower() for day in v]

class GeneralSettings(BaseModel):
    """General organization settings"""
    organization_name: str = Field(..., min_length=1, max_length=255)
    timezone: str = Field(..., description="Default timezone")
    language: str = Field(..., description="Default language")
    date_format: str = Field(..., description="Date format preference")
    currency: str = Field(..., description="Default currency")

class OrganizationSettingsResponse(BaseModel):
    """Organization settings response"""
    id: str
    organization_id: str
    general: GeneralSettings
    business_hours: BusinessHours
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class GeneralSettingsUpdate(BaseModel):
    """General settings update request"""
    organization_name: Optional[str] = Field(None, min_length=1, max_length=255)
    timezone: Optional[str] = None
    language: Optional[str] = None
    date_format: Optional[str] = None
    currency: Optional[str] = None

class BusinessHoursUpdate(BaseModel):
    """Business hours update request"""
    start: Optional[str] = None
    end: Optional[str] = None
    timezone: Optional[str] = None
    workdays: Optional[List[str]] = None
    
    @validator('start', 'end')
    def validate_time_format(cls, v):
        """Validate time format if provided"""
        if v is None:
            return v
        try:
            hour, minute = map(int, v.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError('Invalid time format')
            return v
        except (ValueError, AttributeError):
            raise ValueError('Time must be in HH:MM format')

class OrganizationSettingsUpdate(BaseModel):
    """Complete organization settings update"""
    general: Optional[GeneralSettingsUpdate] = None
    business_hours: Optional[BusinessHoursUpdate] = None

class OrganizationSettingsCreate(BaseModel):
    """Create new organization settings"""
    organization_id: str
    general: GeneralSettings
    business_hours: BusinessHours

# Default settings template
DEFAULT_ORGANIZATION_SETTINGS = {
    "general": {
        "organization_name": "My Organization",
        "timezone": "America/New_York",
        "language": "en-US",
        "date_format": "MM/DD/YYYY",
        "currency": "USD"
    },
    "business_hours": {
        "start": "09:00",
        "end": "18:00",
        "timezone": "America/New_York",
        "workdays": ["monday", "tuesday", "wednesday", "thursday", "friday"]
    }
}
