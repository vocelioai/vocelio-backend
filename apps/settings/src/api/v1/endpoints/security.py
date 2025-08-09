"""
Security Settings Endpoints
Handles security configuration and authentication settings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from ..schemas.security import (
    SecuritySettingsResponse,
    SecuritySettingsUpdate,
    PasswordPolicyUpdate,
    TwoFactorAuthUpdate,
    IPWhitelistUpdate,
    SecurityAuditResponse
)
from ..services.security_service import SecurityService
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=SecuritySettingsResponse)
async def get_security_settings(
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends()
):
    """Get current security settings"""
    try:
        settings = await security_service.get_security_settings(current_user.organization_id)
        return settings
    except Exception as e:
        logger.error(f"Failed to get security settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security settings"
        )

@router.put("/", response_model=SecuritySettingsResponse)
async def update_security_settings(
    settings_update: SecuritySettingsUpdate,
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends()
):
    """Update security settings"""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update security settings"
            )
        
        updated_settings = await security_service.update_security_settings(
            current_user.organization_id,
            settings_update
        )
        
        # Log security change
        await security_service.log_security_event(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            event_type="security_settings_updated",
            details={"updated_fields": list(settings_update.dict(exclude_unset=True).keys())}
        )
        
        logger.info(f"Security settings updated by user {current_user.id}")
        
        return updated_settings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update security settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update security settings"
        )

@router.put("/password-policy", response_model=dict)
async def update_password_policy(
    policy_update: PasswordPolicyUpdate,
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends()
):
    """Update organization password policy"""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update password policy"
            )
        
        await security_service.update_password_policy(
            current_user.organization_id,
            policy_update
        )
        
        # Log policy change
        await security_service.log_security_event(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            event_type="password_policy_updated",
            details=policy_update.dict()
        )
        
        return {"message": "Password policy updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update password policy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password policy"
        )

@router.put("/two-factor-auth", response_model=dict)
async def update_two_factor_auth(
    tfa_update: TwoFactorAuthUpdate,
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends()
):
    """Update two-factor authentication settings"""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update 2FA settings"
            )
        
        await security_service.update_two_factor_auth(
            current_user.organization_id,
            tfa_update
        )
        
        # Log 2FA change
        await security_service.log_security_event(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            event_type="two_factor_auth_updated",
            details={"enabled": tfa_update.enabled, "enforced": tfa_update.enforced}
        )
        
        return {"message": "Two-factor authentication settings updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update 2FA settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update 2FA settings"
        )

@router.put("/ip-whitelist", response_model=dict)
async def update_ip_whitelist(
    whitelist_update: IPWhitelistUpdate,
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends()
):
    """Update IP whitelist settings"""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update IP whitelist"
            )
        
        # Validate IP addresses
        await security_service.validate_ip_addresses(whitelist_update.ip_addresses)
        
        await security_service.update_ip_whitelist(
            current_user.organization_id,
            whitelist_update
        )
        
        # Log IP whitelist change
        await security_service.log_security_event(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            event_type="ip_whitelist_updated",
            details={"ip_addresses": whitelist_update.ip_addresses}
        )
        
        return {"message": "IP whitelist updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update IP whitelist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update IP whitelist"
        )

@router.get("/audit-log", response_model=List[SecurityAuditResponse])
async def get_security_audit_log(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends()
):
    """Get security audit log"""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view security audit log"
            )
        
        audit_log = await security_service.get_security_audit_log(
            current_user.organization_id,
            limit=limit,
            offset=offset
        )
        
        return audit_log
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get security audit log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security audit log"
        )

@router.post("/audit-log/export", response_model=dict)
async def export_security_audit_log(
    start_date: str = None,
    end_date: str = None,
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends()
):
    """Export security audit log to CSV"""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can export security audit log"
            )
        
        export_url = await security_service.export_audit_log(
            current_user.organization_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Log export
        await security_service.log_security_event(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            event_type="security_audit_exported",
            details={"start_date": start_date, "end_date": end_date}
        )
        
        return {"export_url": export_url, "message": "Security audit log exported successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export security audit log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export security audit log"
        )

@router.get("/session-management", response_model=dict)
async def get_active_sessions(
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends()
):
    """Get active user sessions"""
    try:
        sessions = await security_service.get_active_sessions(current_user.organization_id)
        return {"active_sessions": sessions}
    except Exception as e:
        logger.error(f"Failed to get active sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active sessions"
        )

@router.post("/session-management/revoke", response_model=dict)
async def revoke_user_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends()
):
    """Revoke a specific user session"""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can revoke user sessions"
            )
        
        await security_service.revoke_session(session_id)
        
        # Log session revocation
        await security_service.log_security_event(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            event_type="session_revoked",
            details={"session_id": session_id}
        )
        
        return {"message": "Session revoked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke session"
        )

@router.get("/compliance-status", response_model=dict)
async def get_compliance_status(
    current_user: User = Depends(get_current_user),
    security_service: SecurityService = Depends()
):
    """Get organization security compliance status"""
    try:
        compliance_status = await security_service.get_compliance_status(
            current_user.organization_id
        )
        return compliance_status
    except Exception as e:
        logger.error(f"Failed to get compliance status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve compliance status"
        )
