"""
Organization Settings Service
Business logic for organization settings management
"""

from typing import Optional
import logging
from datetime import datetime

from ..models.organization_settings import OrganizationSettings
from ..schemas.organization import (
    OrganizationSettingsResponse,
    OrganizationSettingsUpdate,
    GeneralSettingsUpdate,
    BusinessHoursUpdate,
    DEFAULT_ORGANIZATION_SETTINGS
)
from shared.database.client import get_database
from shared.utils.validation import validate_timezone, validate_currency, validate_language

logger = logging.getLogger(__name__)

class OrganizationService:
    """Service for managing organization settings"""
    
    def __init__(self):
        self.db = get_database()
    
    async def get_organization_settings(self, organization_id: str) -> OrganizationSettingsResponse:
        """Get organization settings by organization ID"""
        try:
            # Query organization settings from database
            response = self.db.table('organization_settings').select('*').eq(
                'organization_id', organization_id
            ).execute()
            
            if not response.data:
                # Create default settings if none exist
                return await self.create_default_settings(organization_id)
            
            settings_data = response.data[0]
            
            # Transform database data to response model
            return OrganizationSettingsResponse(
                id=settings_data['id'],
                organization_id=settings_data['organization_id'],
                general=settings_data['general'],
                business_hours=settings_data['business_hours'],
                created_at=settings_data['created_at'],
                updated_at=settings_data['updated_at']
            )
            
        except Exception as e:
            logger.error(f"Failed to get organization settings: {e}")
            raise
    
    async def create_default_settings(self, organization_id: str) -> OrganizationSettingsResponse:
        """Create default organization settings"""
        try:
            default_data = {
                'organization_id': organization_id,
                'general': DEFAULT_ORGANIZATION_SETTINGS['general'],
                'business_hours': DEFAULT_ORGANIZATION_SETTINGS['business_hours'],
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            response = self.db.table('organization_settings').insert(default_data).execute()
            
            if not response.data:
                raise Exception("Failed to create default settings")
            
            settings_data = response.data[0]
            
            return OrganizationSettingsResponse(
                id=settings_data['id'],
                organization_id=settings_data['organization_id'],
                general=settings_data['general'],
                business_hours=settings_data['business_hours'],
                created_at=settings_data['created_at'],
                updated_at=settings_data['updated_at']
            )
            
        except Exception as e:
            logger.error(f"Failed to create default settings: {e}")
            raise
    
    async def update_organization_settings(
        self, 
        organization_id: str, 
        settings_update: OrganizationSettingsUpdate
    ) -> OrganizationSettingsResponse:
        """Update organization settings"""
        try:
            # Get current settings
            current_settings = await self.get_organization_settings(organization_id)
            
            # Prepare update data
            update_data = {'updated_at': datetime.utcnow().isoformat()}
            
            # Update general settings if provided
            if settings_update.general:
                general_data = current_settings.general.dict()
                general_update = settings_update.general.dict(exclude_unset=True)
                
                # Validate updates
                if 'timezone' in general_update:
                    validate_timezone(general_update['timezone'])
                if 'currency' in general_update:
                    validate_currency(general_update['currency'])
                if 'language' in general_update:
                    validate_language(general_update['language'])
                
                general_data.update(general_update)
                update_data['general'] = general_data
            
            # Update business hours if provided
            if settings_update.business_hours:
                business_hours_data = current_settings.business_hours.dict()
                business_hours_update = settings_update.business_hours.dict(exclude_unset=True)
                
                # Validate timezone if provided
                if 'timezone' in business_hours_update:
                    validate_timezone(business_hours_update['timezone'])
                
                business_hours_data.update(business_hours_update)
                update_data['business_hours'] = business_hours_data
            
            # Update in database
            response = self.db.table('organization_settings').update(update_data).eq(
                'organization_id', organization_id
            ).execute()
            
            if not response.data:
                raise Exception("Failed to update organization settings")
            
            # Return updated settings
            return await self.get_organization_settings(organization_id)
            
        except Exception as e:
            logger.error(f"Failed to update organization settings: {e}")
            raise
    
    async def update_general_settings(
        self, 
        organization_id: str, 
        general_update: GeneralSettingsUpdate
    ):
        """Update only general settings"""
        try:
            current_settings = await self.get_organization_settings(organization_id)
            general_data = current_settings.general.dict()
            
            # Apply updates
            update_dict = general_update.dict(exclude_unset=True)
            
            # Validate updates
            if 'timezone' in update_dict:
                validate_timezone(update_dict['timezone'])
            if 'currency' in update_dict:
                validate_currency(update_dict['currency'])
            if 'language' in update_dict:
                validate_language(update_dict['language'])
            
            general_data.update(update_dict)
            
            # Update in database
            update_data = {
                'general': general_data,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            response = self.db.table('organization_settings').update(update_data).eq(
                'organization_id', organization_id
            ).execute()
            
            if not response.data:
                raise Exception("Failed to update general settings")
                
        except Exception as e:
            logger.error(f"Failed to update general settings: {e}")
            raise
    
    async def update_business_hours(
        self, 
        organization_id: str, 
        business_hours_update: BusinessHoursUpdate
    ):
        """Update only business hours"""
        try:
            current_settings = await self.get_organization_settings(organization_id)
            business_hours_data = current_settings.business_hours.dict()
            
            # Apply updates
            update_dict = business_hours_update.dict(exclude_unset=True)
            
            # Validate timezone if provided
            if 'timezone' in update_dict:
                validate_timezone(update_dict['timezone'])
            
            business_hours_data.update(update_dict)
            
            # Update in database
            update_data = {
                'business_hours': business_hours_data,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            response = self.db.table('organization_settings').update(update_data).eq(
                'organization_id', organization_id
            ).execute()
            
            if not response.data:
                raise Exception("Failed to update business hours")
                
        except Exception as e:
            logger.error(f"Failed to update business hours: {e}")
            raise
    
    async def reset_to_defaults(self, organization_id: str):
        """Reset organization settings to defaults"""
        try:
            # Delete existing settings
            self.db.table('organization_settings').delete().eq(
                'organization_id', organization_id
            ).execute()
            
            # Create new default settings
            await self.create_default_settings(organization_id)
            
            logger.info(f"Organization settings reset to defaults for org {organization_id}")
            
        except Exception as e:
            logger.error(f"Failed to reset organization settings: {e}")
            raise
    
    async def validate_organization_access(self, organization_id: str, user_id: str) -> bool:
        """Validate user has access to organization"""
        try:
            response = self.db.table('users').select('organization_id').eq(
                'id', user_id
            ).execute()
            
            if not response.data:
                return False
            
            return response.data[0]['organization_id'] == organization_id
            
        except Exception as e:
            logger.error(f"Failed to validate organization access: {e}")
            return False
    
    async def get_organization_info(self, organization_id: str) -> dict:
        """Get basic organization information"""
        try:
            response = self.db.table('organizations').select(
                'id, name, created_at, plan_type, status'
            ).eq('id', organization_id).execute()
            
            if not response.data:
                raise Exception("Organization not found")
            
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Failed to get organization info: {e}")
            raise
