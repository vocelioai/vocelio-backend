"""
Security Settings Schemas
Pydantic models for security settings requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import re

class PasswordPolicy(BaseModel):
    """Password policy configuration"""
    min_length: int = Field(ge=6, le=128, description="Minimum password length")
    require_uppercase: bool = Field(description="Require uppercase letters")
    require_lowercase: bool = Field(description="Require lowercase letters")
    require_numbers: bool = Field(description="Require numbers")
    require_symbols: bool = Field(description="Require special symbols")
    max_age_days: Optional[int] = Field(None, ge=1, le=365, description="Password expiry in days")
    prevent_reuse: Optional[int] = Field(None, ge=1, le=24, description="Prevent reusing last N passwords")

class TwoFactorAuth(BaseModel):
    """Two-factor authentication configuration"""
    enabled: bool = Field(description="Enable 2FA")
    enforced: bool = Field(description="Enforce 2FA for all users")
    methods: List[str] = Field(description="Available 2FA methods")
    backup_codes: bool = Field(description="Allow backup codes")
    
    @validator('methods')
    def validate_methods(cls, v):
        """Validate 2FA methods"""
        valid_methods = ['totp', 'sms', 'email', 'hardware_key']
        for method in v:
            if method not in valid_methods:
                raise ValueError(f'Invalid 2FA method: {method}')
        return v

class SessionSecurity(BaseModel):
    """Session security configuration"""
    timeout_minutes: int = Field(ge=5, le=1440, description="Session timeout in minutes")
    max_concurrent_sessions: int = Field(ge=1, le=10, description="Max concurrent sessions per user")
    secure_cookies: bool = Field(description="Use secure cookies")
    same_site_policy: str = Field(description="SameSite cookie policy")
    
    @validator('same_site_policy')
    def validate_same_site_policy(cls, v):
        """Validate SameSite policy"""
        valid_policies = ['strict', 'lax', 'none']
        if v.lower() not in valid_policies:
            raise ValueError(f'Invalid SameSite policy: {v}')
        return v.lower()

class IPWhitelist(BaseModel):
    """IP whitelist configuration"""
    enabled: bool = Field(description="Enable IP whitelisting")
    ip_addresses: List[str] = Field(description="List of allowed IP addresses/CIDR blocks")
    
    @validator('ip_addresses')
    def validate_ip_addresses(cls, v):
        """Validate IP addresses and CIDR blocks"""
        ip_pattern = re.compile(
            r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/(?:[0-9]|[1-2][0-9]|3[0-2]))?$'
        )
        for ip in v:
            if not ip_pattern.match(ip):
                raise ValueError(f'Invalid IP address or CIDR block: {ip}')
        return v

class DataEncryption(BaseModel):
    """Data encryption configuration"""
    at_rest: bool = Field(description="Encrypt data at rest")
    in_transit: bool = Field(description="Encrypt data in transit")
    key_rotation_days: int = Field(ge=30, le=365, description="Key rotation period in days")
    algorithm: str = Field(description="Encryption algorithm")

class SecuritySettingsResponse(BaseModel):
    """Security settings response"""
    id: str
    organization_id: str
    two_factor_auth: TwoFactorAuth
    password_policy: PasswordPolicy
    session_security: SessionSecurity
    ip_whitelist: IPWhitelist
    data_encryption: DataEncryption
    audit_logging: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PasswordPolicyUpdate(BaseModel):
    """Password policy update request"""
    min_length: Optional[int] = Field(None, ge=6, le=128)
    require_uppercase: Optional[bool] = None
    require_lowercase: Optional[bool] = None
    require_numbers: Optional[bool] = None
    require_symbols: Optional[bool] = None
    max_age_days: Optional[int] = Field(None, ge=1, le=365)
    prevent_reuse: Optional[int] = Field(None, ge=1, le=24)

class TwoFactorAuthUpdate(BaseModel):
    """Two-factor authentication update request"""
    enabled: Optional[bool] = None
    enforced: Optional[bool] = None
    methods: Optional[List[str]] = None
    backup_codes: Optional[bool] = None

class SessionSecurityUpdate(BaseModel):
    """Session security update request"""
    timeout_minutes: Optional[int] = Field(None, ge=5, le=1440)
    max_concurrent_sessions: Optional[int] = Field(None, ge=1, le=10)
    secure_cookies: Optional[bool] = None
    same_site_policy: Optional[str] = None

class IPWhitelistUpdate(BaseModel):
    """IP whitelist update request"""
    enabled: Optional[bool] = None
    ip_addresses: Optional[List[str]] = None

class SecuritySettingsUpdate(BaseModel):
    """Complete security settings update"""
    two_factor_auth: Optional[TwoFactorAuthUpdate] = None
    password_policy: Optional[PasswordPolicyUpdate] = None
    session_security: Optional[SessionSecurityUpdate] = None
    ip_whitelist: Optional[IPWhitelistUpdate] = None
    audit_logging: Optional[bool] = None

class SecurityAuditResponse(BaseModel):
    """Security audit log entry"""
    id: str
    organization_id: str
    user_id: str
    user_email: str
    event_type: str
    event_description: str
    ip_address: str
    user_agent: str
    details: dict
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Default security settings
DEFAULT_SECURITY_SETTINGS = {
    "two_factor_auth": {
        "enabled": False,
        "enforced": False,
        "methods": ["totp", "email"],
        "backup_codes": True
    },
    "password_policy": {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_symbols": False,
        "max_age_days": None,
        "prevent_reuse": None
    },
    "session_security": {
        "timeout_minutes": 60,
        "max_concurrent_sessions": 3,
        "secure_cookies": True,
        "same_site_policy": "lax"
    },
    "ip_whitelist": {
        "enabled": False,
        "ip_addresses": []
    },
    "data_encryption": {
        "at_rest": True,
        "in_transit": True,
        "key_rotation_days": 90,
        "algorithm": "AES-256"
    },
    "audit_logging": True
}
