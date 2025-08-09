# apps/team-hub/src/api/v1/api.py

from fastapi import APIRouter

from api.v1.endpoints import users, teams, dashboard, invitations, roles

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])  
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(invitations.router, prefix="/invitations", tags=["invitations"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])

# apps/team-hub/src/api/v1/endpoints/invitations.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from shared.database.client import get_database
from shared.auth.dependencies import get_current_user, require_permissions
from schemas.invitation import InvitationCreate, InvitationUpdate, InvitationResponse, InvitationStatus
from schemas.response import APIResponse, PaginatedResponse, PaginationMeta
from services.invitation_service import InvitationService
from models.user import User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_invitations(
    status: Optional[InvitationStatus] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of invitations"""
    
    invitation_service = InvitationService(db)
    
    try:
        invitations, total_count = await invitation_service.get_invitations_with_filters(
            current_user.organization_id, status, page, size
        )
        
        total_pages = (total_count + size - 1) // size
        has_next = page < total_pages
        has_prev = page > 1
        
        return PaginatedResponse(
            data=[InvitationResponse.from_orm(inv) for inv in invitations],
            meta=PaginationMeta(
                page=page,
                size=size,
                total=total_count,
                pages=total_pages,
                has_next=has_next,
                has_prev=has_prev
            )
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=APIResponse, status_code=201)
async def create_invitation(
    invitation_data: InvitationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["invitation:create"]))
):
    """Create a new team invitation"""
    
    invitation_service = InvitationService(db)
    
    # Set organization and inviter from current user
    invitation_data.organization_id = current_user.organization_id
    invitation_data.invited_by_id = current_user.id
    
    try:
        new_invitation = await invitation_service.create_invitation(invitation_data)
        
        # Add background task for sending invitation email
        # background_tasks.add_task(send_invitation_email, new_invitation.email, new_invitation.id)
        
        return APIResponse(
            message="Invitation created successfully",
            data=InvitationResponse.from_orm(new_invitation)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{invitation_id}", response_model=APIResponse)
async def get_invitation(
    invitation_id: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get invitation by ID"""
    
    invitation_service = InvitationService(db)
    invitation = await invitation_service.get_invitation_by_id(invitation_id)
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Check if invitation belongs to same organization
    if invitation.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return APIResponse(
        message="Invitation retrieved successfully",
        data=InvitationResponse.from_orm(invitation)
    )

@router.patch("/{invitation_id}", response_model=APIResponse)
async def update_invitation_status(
    invitation_id: str,
    invitation_update: InvitationUpdate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Update invitation status (accept/decline)"""
    
    invitation_service = InvitationService(db)
    
    try:
        updated_invitation = await invitation_service.update_invitation_status(
            invitation_id, invitation_update.status
        )
        
        return APIResponse(
            message="Invitation status updated successfully",
            data=InvitationResponse.from_orm(updated_invitation)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{invitation_id}", response_model=APIResponse)
async def cancel_invitation(
    invitation_id: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["invitation:delete"]))
):
    """Cancel an invitation"""
    
    invitation_service = InvitationService(db)
    
    try:
        await invitation_service.cancel_invitation(invitation_id, current_user.organization_id)
        
        return APIResponse(
            message="Invitation cancelled successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{invitation_id}/resend", response_model=APIResponse)
async def resend_invitation(
    invitation_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["invitation:resend"]))
):
    """Resend an invitation email"""
    
    invitation_service = InvitationService(db)
    
    try:
        invitation = await invitation_service.get_invitation_by_id(invitation_id)
        
        if not invitation:
            raise HTTPException(status_code=404, detail="Invitation not found")
        
        if invitation.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if invitation.status != InvitationStatus.PENDING:
            raise HTTPException(status_code=400, detail="Can only resend pending invitations")
        
        # Add background task for resending invitation email
        # background_tasks.add_task(resend_invitation_email, invitation.email, invitation.id)
        
        return APIResponse(
            message="Invitation resent successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# apps/team-hub/src/api/v1/endpoints/roles.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from shared.database.client import get_database
from shared.auth.dependencies import get_current_user, require_permissions
from schemas.role import RoleCreate, RoleUpdate, RoleResponse
from schemas.response import APIResponse
from services.role_service import RoleService
from models.user import User

router = APIRouter()

@router.get("/", response_model=APIResponse)
async def get_roles(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get all roles in organization"""
    
    role_service = RoleService(db)
    
    try:
        roles = await role_service.get_roles_by_organization(current_user.organization_id)
        
        return APIResponse(
            message="Roles retrieved successfully",
            data=[RoleResponse.from_orm(role) for role in roles]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=APIResponse, status_code=201)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["role:create"]))
):
    """Create a new role"""
    
    role_service = RoleService(db)
    
    # Set organization from current user
    role_data.organization_id = current_user.organization_id
    
    try:
        new_role = await role_service.create_role(role_data)
        
        return APIResponse(
            message="Role created successfully",
            data=RoleResponse.from_orm(new_role)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{role_id}", response_model=APIResponse)
async def get_role(
    role_id: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get role by ID"""
    
    role_service = RoleService(db)
    role = await role_service.get_role_by_id(role_id)
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if role belongs to same organization
    if role.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return APIResponse(
        message="Role retrieved successfully",
        data=RoleResponse.from_orm(role)
    )

@router.put("/{role_id}", response_model=APIResponse)
async def update_role(
    role_id: str,
    role_data: RoleUpdate,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["role:update"]))
):
    """Update role information"""
    
    role_service = RoleService(db)
    
    try:
        updated_role = await role_service.update_role(role_id, role_data, current_user.organization_id)
        
        return APIResponse(
            message="Role updated successfully",
            data=RoleResponse.from_orm(updated_role)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{role_id}", response_model=APIResponse)
async def delete_role(
    role_id: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(require_permissions(["role:delete"]))
):
    """Delete a role"""
    
    role_service = RoleService(db)
    
    try:
        await role_service.delete_role(role_id, current_user.organization_id)
        
        return APIResponse(
            message="Role deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/permissions/available", response_model=APIResponse)
async def get_available_permissions(
    current_user: User = Depends(get_current_user)
):
    """Get list of available permissions"""
    
    # In a real implementation, this would come from a permission registry
    available_permissions = [
        # User permissions
        "user:create", "user:read", "user:update", "user:delete",
        # Team permissions  
        "team:create", "team:read", "team:update", "team:delete",
        "team:manage_members", "team:manage_leadership",
        # Role permissions
        "role:create", "role:read", "role:update", "role:delete",
        # Invitation permissions
        "invitation:create", "invitation:read", "invitation:delete", "invitation:resend",
        # Dashboard permissions
        "dashboard:view_analytics", "dashboard:export_reports",
        # Admin permissions
        "admin:full_access", "admin:user_management", "admin:system_settings"
    ]
    
    return APIResponse(
        message="Available permissions retrieved successfully",
        data=available_permissions
    )

# apps/team-hub/src/services/invitation_service.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import logging

from models.invitation import Invitation, InvitationStatus
from schemas.invitation import InvitationCreate
from shared.exceptions.service import ServiceException

logger = logging.getLogger(__name__)

class InvitationService:
    def __init__(self, db: Session):
        self.db = db

    async def create_invitation(self, invitation_data: InvitationCreate) -> Invitation:
        """Create a new invitation"""
        try:
            # Check if active invitation already exists for this email
            existing_invitation = self.db.query(Invitation).filter(
                and_(
                    Invitation.email == invitation_data.email,
                    Invitation.organization_id == invitation_data.organization_id,
                    Invitation.status == InvitationStatus.PENDING
                )
            ).first()
            
            if existing_invitation:
                raise ServiceException("Active invitation already exists for this email")
            
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(hours=invitation_data.expires_in_hours)
            
            # Create new invitation
            invitation = Invitation(
                organization_id=invitation_data.organization_id,
                email=invitation_data.email,
                role=invitation_data.role,
                department=invitation_data.department,
                invited_by_id=invitation_data.invited_by_id,
                expires_at=expires_at
            )
            
            self.db.add(invitation)
            self.db.commit()
            self.db.refresh(invitation)
            
            logger.info(f"Created invitation for: {invitation.email}")
            return invitation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating invitation: {str(e)}")
            raise ServiceException(f"Failed to create invitation: {str(e)}")

    async def get_invitation_by_id(self, invitation_id: str) -> Optional[Invitation]:
        """Get invitation by ID"""
        try:
            invitation = self.db.query(Invitation).filter(
                Invitation.id == invitation_id
            ).first()
            return invitation
        except Exception as e:
            logger.error(f"Error fetching invitation {invitation_id}: {str(e)}")
            raise ServiceException(f"Failed to fetch invitation: {str(e)}")

    async def get_invitations_with_filters(
        self, 
        organization_id: str, 
        status: Optional[InvitationStatus], 
        page: int, 
        size: int
    ) -> Tuple[List[Invitation], int]:
        """Get invitations with filtering and pagination"""
        try:
            query = self.db.query(Invitation).filter(
                Invitation.organization_id == organization_id
            )
            
            if status:
                query = query.filter(Invitation.status == status)
            
            total_count = query.count()
            
            # Apply pagination and ordering
            offset = (page - 1) * size
            invitations = query.order_by(desc(Invitation.created_at)).offset(offset).limit(size).all()
            
            return invitations, total_count
        except Exception as e:
            logger.error(f"Error fetching invitations: {str(e)}")
            raise ServiceException(f"Failed to fetch invitations: {str(e)}")

    async def update_invitation_status(self, invitation_id: str, status: InvitationStatus) -> Invitation:
        """Update invitation status"""
        try:
            invitation = await self.get_invitation_by_id(invitation_id)
            if not invitation:
                raise ServiceException("Invitation not found")
            
            # Check if invitation is still valid
            if invitation.expires_at < datetime.utcnow():
                invitation.status = InvitationStatus.EXPIRED
                raise ServiceException("Invitation has expired")
            
            invitation.status = status
            invitation.updated_at = datetime.utcnow()
            
            if status == InvitationStatus.ACCEPTED:
                invitation.accepted_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(invitation)
            
            logger.info(f"Updated invitation status: {invitation_id} -> {status}")
            return invitation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating invitation status: {str(e)}")
            raise ServiceException(f"Failed to update invitation status: {str(e)}")

    async def cancel_invitation(self, invitation_id: str, organization_id: str) -> bool:
        """Cancel an invitation"""
        try:
            invitation = await self.get_invitation_by_id(invitation_id)
            if not invitation:
                raise ServiceException("Invitation not found")
            
            if invitation.organization_id != organization_id:
                raise ServiceException("Access denied")
            
            if invitation.status != InvitationStatus.PENDING:
                raise ServiceException("Can only cancel pending invitations")
            
            invitation.status = InvitationStatus.EXPIRED
            invitation.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Cancelled invitation: {invitation_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cancelling invitation: {str(e)}")
            raise ServiceException(f"Failed to cancel invitation: {str(e)}")

# apps/team-hub/src/services/role_service.py

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
import logging

from models.role import Role
from schemas.role import RoleCreate, RoleUpdate
from shared.exceptions.service import ServiceException

logger = logging.getLogger(__name__)

class RoleService:
    def __init__(self, db: Session):
        self.db = db

    async def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role"""
        try:
            # Check if role name already exists in organization
            existing_role = self.db.query(Role).filter(
                and_(
                    Role.name == role_data.name,
                    Role.organization_id == role_data.organization_id,
                    Role.is_active == True
                )
            ).first()
            
            if existing_role:
                raise ServiceException("Role with this name already exists")
            
            # Create new role
            role = Role(
                organization_id=role_data.organization_id,
                name=role_data.name,
                description=role_data.description,
                permissions=role_data.permissions
            )
            
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
            
            logger.info(f"Created new role: {role.name}")
            return role
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating role: {str(e)}")
            raise ServiceException(f"Failed to create role: {str(e)}")

    async def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID"""
        try:
            role = self.db.query(Role).filter(
                and_(Role.id == role_id, Role.is_active == True)
            ).first()
            return role
        except Exception as e:
            logger.error(f"Error fetching role {role_id}: {str(e)}")
            raise ServiceException(f"Failed to fetch role: {str(e)}")

    async def get_roles_by_organization(self, organization_id: str) -> List[Role]:
        """Get all roles in organization"""
        try:
            roles = self.db.query(Role).filter(
                and_(Role.organization_id == organization_id, Role.is_active == True)
            ).all()
            return roles
        except Exception as e:
            logger.error(f"Error fetching roles for organization {organization_id}: {str(e)}")
            raise ServiceException(f"Failed to fetch roles: {str(e)}")

    async def update_role(self, role_id: str, role_data: RoleUpdate, organization_id: str) -> Role:
        """Update role information"""
        try:
            role = await self.get_role_by_id(role_id)
            if not role:
                raise ServiceException("Role not found")
            
            if role.organization_id != organization_id:
                raise ServiceException("Access denied")
            
            # Update fields if provided
            update_data = role_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(role, field, value)
            
            role.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(role)
            
            logger.info(f"Updated role: {role.name}")
            return role
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating role {role_id}: {str(e)}")
            raise ServiceException(f"Failed to update role: {str(e)}")

    async def delete_role(self, role_id: str, organization_id: str) -> bool:
        """Soft delete a role"""
        try:
            role = await self.get_role_by_id(role_id)
            if not role:
                raise ServiceException("Role not found")
            
            if role.organization_id != organization_id:
                raise ServiceException("Access denied")
            
            role.is_active = False
            role.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Deleted role: {role.name}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting role {role_id}: {str(e)}")
            raise ServiceException(f"Failed to delete role: {str(e)}")