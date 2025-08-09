# apps/team-hub/src/services/user_service.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

from models.user import User, UserStatus
from models.team import Team
from models.team_membership import TeamMembership
from schemas.user import UserCreate, UserUpdate, UserFilters
from shared.exceptions.service import ServiceException
from shared.utils.encryption import hash_password, verify_password

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = self.db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise ServiceException("User with this email already exists")
            
            # Create new user
            user = User(
                organization_id=user_data.organization_id,
                name=user_data.name,
                email=user_data.email,
                phone_number=user_data.phone_number,
                avatar=user_data.avatar,
                role=user_data.role,
                department=user_data.department,
                location=user_data.location,
                timezone=user_data.timezone,
                skills=user_data.skills,
                certifications=user_data.certifications,
                status=UserStatus.OFFLINE,
                performance_score=0.0,
                calls_today=0,
                avg_call_duration=0,
                customer_satisfaction=0.0
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Created new user: {user.email}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise ServiceException(f"Failed to create user: {str(e)}")

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user = self.db.query(User).filter(
                and_(User.id == user_id, User.is_active == True)
            ).first()
            return user
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {str(e)}")
            raise ServiceException(f"Failed to fetch user: {str(e)}")

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            user = self.db.query(User).filter(
                and_(User.email == email, User.is_active == True)
            ).first()
            return user
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {str(e)}")
            raise ServiceException(f"Failed to fetch user: {str(e)}")

    async def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """Update user information"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise ServiceException("User not found")
            
            # Update fields if provided
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Updated user: {user.email}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise ServiceException(f"Failed to update user: {str(e)}")

    async def update_user_status(self, user_id: str, status: UserStatus) -> User:
        """Update user status"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise ServiceException("User not found")
            
            user.status = status
            user.last_activity = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Updated user status: {user.email} -> {status}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user status {user_id}: {str(e)}")
            raise ServiceException(f"Failed to update user status: {str(e)}")

    async def get_users_with_filters(self, filters: UserFilters, organization_id: str) -> Tuple[List[User], int]:
        """Get users with filtering, searching, and pagination"""
        try:
            # Base query
            query = self.db.query(User).filter(
                and_(
                    User.organization_id == organization_id,
                    User.is_active == True
                )
            )
            
            # Apply filters
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        User.name.ilike(search_term),
                        User.email.ilike(search_term),
                        User.role.ilike(search_term),
                        User.department.ilike(search_term)
                    )
                )
            
            if filters.role:
                query = query.filter(User.role == filters.role)
            
            if filters.department:
                query = query.filter(User.department == filters.department)
            
            if filters.status:
                query = query.filter(User.status == filters.status)
            
            if filters.location:
                query = query.filter(User.location.ilike(f"%{filters.location}%"))
            
            if filters.min_performance is not None:
                query = query.filter(User.performance_score >= filters.min_performance)
            
            if filters.max_performance is not None:
                query = query.filter(User.performance_score <= filters.max_performance)
            
            if filters.skills:
                for skill in filters.skills:
                    query = query.filter(User.skills.contains([skill]))
            
            if filters.certifications:
                for cert in filters.certifications:
                    query = query.filter(User.certifications.contains([cert]))
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply sorting
            sort_column = getattr(User, filters.sort_by, User.name)
            if filters.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Apply pagination
            offset = (filters.page - 1) * filters.size
            users = query.offset(offset).limit(filters.size).all()
            
            return users, total_count
            
        except Exception as e:
            logger.error(f"Error fetching users with filters: {str(e)}")
            raise ServiceException(f"Failed to fetch users: {str(e)}")

    async def get_team_metrics(self, organization_id: str) -> Dict[str, Any]:
        """Get comprehensive team metrics"""
        try:
            # Get all active users
            users = self.db.query(User).filter(
                and_(User.organization_id == organization_id, User.is_active == True)
            ).all()
            
            total_members = len(users)
            
            # Status counts
            status_counts = {
                "active_today": 0,
                "on_break": 0,
                "offline": 0,
                "online": 0,
                "on_call": 0,
                "training": 0
            }
            
            # Performance metrics
            total_performance = 0
            total_calls_today = 0
            total_call_duration = 0
            total_satisfaction = 0
            
            for user in users:
                # Count status
                if user.status == UserStatus.ONLINE:
                    status_counts["active_today"] += 1
                    status_counts["online"] += 1
                elif user.status == UserStatus.ON_CALL:
                    status_counts["active_today"] += 1
                    status_counts["on_call"] += 1
                elif user.status == UserStatus.BREAK:
                    status_counts["on_break"] += 1
                elif user.status == UserStatus.TRAINING:
                    status_counts["training"] += 1
                elif user.status == UserStatus.OFFLINE:
                    status_counts["offline"] += 1
                
                # Aggregate metrics
                total_performance += user.performance_score
                total_calls_today += user.calls_today
                total_call_duration += user.avg_call_duration
                total_satisfaction += user.customer_satisfaction
            
            # Calculate averages
            avg_performance = total_performance / total_members if total_members > 0 else 0
            avg_call_duration = total_call_duration / total_members if total_members > 0 else 0
            avg_satisfaction = total_satisfaction / total_members if total_members > 0 else 0
            
            # Mock additional metrics (would come from other services in real implementation)
            trainings_completed = 89  # Would be calculated from training service
            certification_rate = 97.3  # Would be calculated from certification data
            
            return {
                "total_members": total_members,
                "active_today": status_counts["active_today"],
                "on_break": status_counts["on_break"],
                "offline": status_counts["offline"],
                "avg_performance": round(avg_performance, 1),
                "total_calls_today": total_calls_today,
                "avg_call_duration": int(avg_call_duration),
                "customer_satisfaction": round(avg_satisfaction, 1),
                "trainings_completed": trainings_completed,
                "certification_rate": certification_rate,
                "status_breakdown": status_counts
            }
            
        except Exception as e:
            logger.error(f"Error calculating team metrics: {str(e)}")
            raise ServiceException(f"Failed to calculate team metrics: {str(e)}")

    async def get_department_summary(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get department summary with counts and growth"""
        try:
            # Query department statistics
            dept_stats = self.db.query(
                User.department,
                func.count(User.id).label('count'),
                func.avg(User.performance_score).label('avg_performance')
            ).filter(
                and_(User.organization_id == organization_id, User.is_active == True)
            ).group_by(User.department).all()
            
            # Mock growth data (would come from historical data in real implementation)
            growth_data = {
                'Operations': 12.3,
                'Sales': 8.7,
                'Customer Success': 15.2,
                'Technology': 22.1,
                'Legal & Compliance': 5.8,
                'Quality': 18.9
            }
            
            color_map = {
                'Operations': 'blue',
                'Sales': 'green',
                'Customer Success': 'purple',
                'Technology': 'orange',
                'Legal & Compliance': 'red',
                'Quality': 'cyan'
            }
            
            departments = []
            for dept_stat in dept_stats:
                departments.append({
                    "name": dept_stat.department,
                    "count": dept_stat.count,
                    "growth": growth_data.get(dept_stat.department, 0.0),
                    "color": color_map.get(dept_stat.department, 'gray'),
                    "avg_performance": round(dept_stat.avg_performance or 0, 1)
                })
            
            return departments
            
        except Exception as e:
            logger.error(f"Error fetching department summary: {str(e)}")
            raise ServiceException(f"Failed to fetch department summary: {str(e)}")

    async def delete_user(self, user_id: str) -> bool:
        """Soft delete a user"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise ServiceException("User not found")
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Deleted user: {user.email}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise ServiceException(f"Failed to delete user: {str(e)}")

    async def get_available_roles(self, organization_id: str) -> List[str]:
        """Get list of available roles in organization"""
        try:
            roles = self.db.query(User.role).filter(
                and_(User.organization_id == organization_id, User.is_active == True)
            ).distinct().all()
            
            return [role[0] for role in roles if role[0]]
            
        except Exception as e:
            logger.error(f"Error fetching available roles: {str(e)}")
            raise ServiceException(f"Failed to fetch available roles: {str(e)}")

    async def get_available_departments(self, organization_id: str) -> List[str]:
        """Get list of available departments in organization"""
        try:
            departments = self.db.query(User.department).filter(
                and_(User.organization_id == organization_id, User.is_active == True)
            ).distinct().all()
            
            return [dept[0] for dept in departments if dept[0]]
            
        except Exception as e:
            logger.error(f"Error fetching available departments: {str(e)}")
            raise ServiceException(f"Failed to fetch available departments: {str(e)}")

    async def update_performance_metrics(self, user_id: str, metrics: Dict[str, Any]) -> User:
        """Update user performance metrics"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise ServiceException("User not found")
            
            # Update metrics if provided
            if "performance_score" in metrics:
                user.performance_score = metrics["performance_score"]
            if "calls_today" in metrics:
                user.calls_today = metrics["calls_today"]
            if "avg_call_duration" in metrics:
                user.avg_call_duration = metrics["avg_call_duration"]
            if "customer_satisfaction" in metrics:
                user.customer_satisfaction = metrics["customer_satisfaction"]
            
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Updated performance metrics for user: {user.email}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating performance metrics for user {user_id}: {str(e)}")
            raise ServiceException(f"Failed to update performance metrics: {str(e)}")

    