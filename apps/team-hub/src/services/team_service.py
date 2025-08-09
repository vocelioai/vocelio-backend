# apps/team-hub/src/services/team_service.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging

from models.team import Team
from models.user import User
from models.team_membership import TeamMembership
from schemas.team import TeamCreate, TeamUpdate, TeamFilters
from shared.exceptions.service import ServiceException

logger = logging.getLogger(__name__)

class TeamService:
    def __init__(self, db: Session):
        self.db = db

    async def create_team(self, team_data: TeamCreate) -> Team:
        """Create a new team"""
        try:
            # Check if team name already exists in organization
            existing_team = self.db.query(Team).filter(
                and_(
                    Team.name == team_data.name,
                    Team.organization_id == team_data.organization_id,
                    Team.is_active == True
                )
            ).first()
            
            if existing_team:
                raise ServiceException("Team with this name already exists")
            
            # Validate team lead if provided
            if team_data.team_lead_id:
                team_lead = self.db.query(User).filter(
                    and_(
                        User.id == team_data.team_lead_id,
                        User.organization_id == team_data.organization_id,
                        User.is_active == True
                    )
                ).first()
                
                if not team_lead:
                    raise ServiceException("Invalid team lead user")
            
            # Create new team
            team = Team(
                organization_id=team_data.organization_id,
                name=team_data.name,
                description=team_data.description,
                department=team_data.department,
                team_lead_id=team_data.team_lead_id,
                performance_score=0.0,
                total_calls_today=0,
                avg_satisfaction=0.0,
                member_count=0
            )
            
            self.db.add(team)
            self.db.commit()
            self.db.refresh(team)
            
            logger.info(f"Created new team: {team.name}")
            return team
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating team: {str(e)}")
            raise ServiceException(f"Failed to create team: {str(e)}")

    async def get_team_by_id(self, team_id: str, include_members: bool = False) -> Optional[Team]:
        """Get team by ID with optional member details"""
        try:
            query = self.db.query(Team)
            
            if include_members:
                query = query.options(
                    joinedload(Team.team_lead),
                    joinedload(Team.memberships).joinedload(TeamMembership.user)
                )
            
            team = query.filter(
                and_(Team.id == team_id, Team.is_active == True)
            ).first()
            
            return team
            
        except Exception as e:
            logger.error(f"Error fetching team {team_id}: {str(e)}")
            raise ServiceException(f"Failed to fetch team: {str(e)}")

    async def update_team(self, team_id: str, team_data: TeamUpdate) -> Team:
        """Update team information"""
        try:
            team = await self.get_team_by_id(team_id)
            if not team:
                raise ServiceException("Team not found")
            
            # Validate team lead if provided
            if team_data.team_lead_id:
                team_lead = self.db.query(User).filter(
                    and_(
                        User.id == team_data.team_lead_id,
                        User.organization_id == team.organization_id,
                        User.is_active == True
                    )
                ).first()
                
                if not team_lead:
                    raise ServiceException("Invalid team lead user")
            
            # Update fields if provided
            update_data = team_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(team, field, value)
            
            team.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(team)
            
            logger.info(f"Updated team: {team.name}")
            return team
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating team {team_id}: {str(e)}")
            raise ServiceException(f"Failed to update team: {str(e)}")

    async def get_teams_with_filters(self, filters: TeamFilters, organization_id: str) -> Tuple[List[Team], int]:
        """Get teams with filtering, searching, and pagination"""
        try:
            # Base query
            query = self.db.query(Team).filter(
                and_(
                    Team.organization_id == organization_id,
                    Team.is_active == True
                )
            )
            
            # Apply filters
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Team.name.ilike(search_term),
                        Team.description.ilike(search_term),
                        Team.department.ilike(search_term)
                    )
                )
            
            if filters.department:
                query = query.filter(Team.department == filters.department)
            
            if filters.min_size is not None:
                query = query.filter(Team.member_count >= filters.min_size)
            
            if filters.max_size is not None:
                query = query.filter(Team.member_count <= filters.max_size)
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply sorting
            sort_column = getattr(Team, filters.sort_by, Team.name)
            if filters.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Apply pagination
            offset = (filters.page - 1) * filters.size
            teams = query.offset(offset).limit(filters.size).all()
            
            return teams, total_count
            
        except Exception as e:
            logger.error(f"Error fetching teams with filters: {str(e)}")
            raise ServiceException(f"Failed to fetch teams: {str(e)}")

    async def add_member_to_team(self, team_id: str, user_id: str, role_in_team: Optional[str] = None) -> TeamMembership:
        """Add a user to a team"""
        try:
            # Validate team exists
            team = await self.get_team_by_id(team_id)
            if not team:
                raise ServiceException("Team not found")
            
            # Validate user exists and is in same organization
            user = self.db.query(User).filter(
                and_(
                    User.id == user_id,
                    User.organization_id == team.organization_id,
                    User.is_active == True
                )
            ).first()
            
            if not user:
                raise ServiceException("User not found or not in same organization")
            
            # Check if user is already in team
            existing_membership = self.db.query(TeamMembership).filter(
                and_(
                    TeamMembership.team_id == team_id,
                    TeamMembership.user_id == user_id,
                    TeamMembership.is_active == True
                )
            ).first()
            
            if existing_membership:
                raise ServiceException("User is already a member of this team")
            
            # Create team membership
            membership = TeamMembership(
                team_id=team_id,
                user_id=user_id,
                role_in_team=role_in_team
            )
            
            self.db.add(membership)
            
            # Update team member count
            team.member_count = self.db.query(TeamMembership).filter(
                and_(TeamMembership.team_id == team_id, TeamMembership.is_active == True)
            ).count() + 1
            
            team.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(membership)
            
            logger.info(f"Added user {user_id} to team {team_id}")
            return membership
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding member to team: {str(e)}")
            raise ServiceException(f"Failed to add member to team: {str(e)}")

    async def remove_member_from_team(self, team_id: str, user_id: str) -> bool:
        """Remove a user from a team"""
        try:
            # Find membership
            membership = self.db.query(TeamMembership).filter(
                and_(
                    TeamMembership.team_id == team_id,
                    TeamMembership.user_id == user_id,
                    TeamMembership.is_active == True
                )
            ).first()
            
            if not membership:
                raise ServiceException("User is not a member of this team")
            
            # Deactivate membership
            membership.is_active = False
            
            # Update team member count
            team = await self.get_team_by_id(team_id)
            if team:
                team.member_count = self.db.query(TeamMembership).filter(
                    and_(TeamMembership.team_id == team_id, TeamMembership.is_active == True)
                ).count() - 1
                team.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Removed user {user_id} from team {team_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing member from team: {str(e)}")
            raise ServiceException(f"Failed to remove member from team: {str(e)}")

    async def get_team_members(self, team_id: str) -> List[User]:
        """Get all active members of a team"""
        try:
            members = self.db.query(User).join(
                TeamMembership, User.id == TeamMembership.user_id
            ).filter(
                and_(
                    TeamMembership.team_id == team_id,
                    TeamMembership.is_active == True,
                    User.is_active == True
                )
            ).all()
            
            return members
            
        except Exception as e:
            logger.error(f"Error fetching team members for team {team_id}: {str(e)}")
            raise ServiceException(f"Failed to fetch team members: {str(e)}")

    async def update_team_metrics(self, team_id: str) -> Team:
        """Update team performance metrics based on member data"""
        try:
            team = await self.get_team_by_id(team_id)
            if not team:
                raise ServiceException("Team not found")
            
            # Get all active team members
            members = await self.get_team_members(team_id)
            
            if members:
                # Calculate aggregated metrics
                total_performance = sum(member.performance_score for member in members)
                total_calls = sum(member.calls_today for member in members)
                total_satisfaction = sum(member.customer_satisfaction for member in members)
                
                team.performance_score = total_performance / len(members)
                team.total_calls_today = total_calls
                team.avg_satisfaction = total_satisfaction / len(members)
                team.member_count = len(members)
            else:
                team.performance_score = 0.0
                team.total_calls_today = 0
                team.avg_satisfaction = 0.0
                team.member_count = 0
            
            team.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(team)
            
            logger.info(f"Updated metrics for team: {team.name}")
            return team
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating team metrics for team {team_id}: {str(e)}")
            raise ServiceException(f"Failed to update team metrics: {str(e)}")

    async def delete_team(self, team_id: str) -> bool:
        """Soft delete a team and deactivate all memberships"""
        try:
            team = await self.get_team_by_id(team_id)
            if not team:
                raise ServiceException("Team not found")
            
            # Deactivate team
            team.is_active = False
            team.updated_at = datetime.utcnow()
            
            # Deactivate all memberships
            self.db.query(TeamMembership).filter(
                TeamMembership.team_id == team_id
            ).update({"is_active": False})
            
            self.db.commit()
            
            logger.info(f"Deleted team: {team.name}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting team {team_id}: {str(e)}")
            raise ServiceException(f"Failed to delete team: {str(e)}")

    async def get_user_teams(self, user_id: str) -> List[Team]:
        """Get all teams a user belongs to"""
        try:
            teams = self.db.query(Team).join(
                TeamMembership, Team.id == TeamMembership.team_id
            ).filter(
                and_(
                    TeamMembership.user_id == user_id,
                    TeamMembership.is_active == True,
                    Team.is_active == True
                )
            ).all()
            
            return teams
            
        except Exception as e:
            logger.error(f"Error fetching teams by department: {str(e)}")
            raise ServiceException(f"Failed to fetch teams by department: {str(e)}")

    async def transfer_team_leadership(self, team_id: str, new_lead_id: str) -> Team:
        """Transfer team leadership to another member"""
        try:
            team = await self.get_team_by_id(team_id)
            if not team:
                raise ServiceException("Team not found")
            
            # Validate new lead is a member of the team
            membership = self.db.query(TeamMembership).filter(
                and_(
                    TeamMembership.team_id == team_id,
                    TeamMembership.user_id == new_lead_id,
                    TeamMembership.is_active == True
                )
            ).first()
            
            if not membership:
                raise ServiceException("New lead must be a member of the team")
            
            # Update team lead
            team.team_lead_id = new_lead_id
            team.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(team)
            
            logger.info(f"Transferred leadership of team {team_id} to user {new_lead_id}")
            return team
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error transferring team leadership: {str(e)}")
            raise ServiceException(f"Failed to transfer team leadership: {str(e)}") fetching teams for user {user_id}: {str(e)}")
            raise ServiceException(f"Failed to fetch user teams: {str(e)}")

    async def get_teams_by_department(self, organization_id: str, department: str) -> List[Team]:
        """Get all teams in a specific department"""
        try:
            teams = self.db.query(Team).filter(
                and_(
                    Team.organization_id == organization_id,
                    Team.department == department,
                    Team.is_active == True
                )
            ).all()
            
            return teams
            
        except Exception as e:
            logger.error(f"Error