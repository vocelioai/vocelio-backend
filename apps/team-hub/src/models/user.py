# apps/team-hub/src/models/user.py

from sqlalchemy import Column, String, DateTime, Boolean, Float, Integer, Text, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class UserStatus(str, enum.Enum):
    ONLINE = "online"
    ON_CALL = "on-call"
    BREAK = "break"
    TRAINING = "training"
    OFFLINE = "offline"

class User(Base):
    __tablename__ = "users"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: f"usr_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone_number = Column(String(20), nullable=True)
    avatar = Column(String(10), default="👤")  # Emoji avatar
    
    # Role and department
    role = Column(String(100), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    
    # Status and activity
    status = Column(Enum(UserStatus), default=UserStatus.OFFLINE, index=True)
    last_login = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Location and timezone
    location = Column(String(100), nullable=True)
    timezone = Column(String(50), default="UTC")
    
    # Performance metrics
    performance_score = Column(Float, default=0.0)
    calls_today = Column(Integer, default=0)
    avg_call_duration = Column(Integer, default=0)  # in seconds
    customer_satisfaction = Column(Float, default=0.0)
    
    # Skills and certifications (stored as JSON arrays)
    skills = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    
    # Metadata
    join_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="members")
    team_memberships = relationship("TeamMembership", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.name} ({self.email})>"

# apps/team-hub/src/models/team.py

class Team(Base):
    __tablename__ = "teams"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: f"team_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    department = Column(String(100), nullable=False, index=True)
    
    # Team lead
    team_lead_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Performance metrics
    performance_score = Column(Float, default=0.0)
    total_calls_today = Column(Integer, default=0)
    avg_satisfaction = Column(Float, default=0.0)
    member_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="teams")
    team_lead = relationship("User", foreign_keys=[team_lead_id])
    memberships = relationship("TeamMembership", back_populates="team")
    
    def __repr__(self):
        return f"<Team {self.name} ({self.department})>"

# apps/team-hub/src/models/team_membership.py

class TeamMembership(Base):
    __tablename__ = "team_memberships"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: f"tmem_{uuid.uuid4().hex[:12]}")
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Membership details
    role_in_team = Column(String(100), nullable=True)  # Team-specific role
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    team = relationship("Team", back_populates="memberships")
    user = relationship("User", back_populates="team_memberships")
    
    def __repr__(self):
        return f"<TeamMembership {self.user_id} in {self.team_id}>"

# apps/team-hub/src/models/organization.py

class Organization(Base):
    __tablename__ = "organizations"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: f"org_{uuid.uuid4().hex[:12]}")
    
    # Basic information
    name = Column(String(255), nullable=False)
    domain = Column(String(100), nullable=True, unique=True)
    logo_url = Column(String(500), nullable=True)
    
    # Contact information
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    
    # Settings
    timezone = Column(String(50), default="UTC")
    settings = Column(JSON, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    members = relationship("User", back_populates="organization")
    teams = relationship("Team", back_populates="organization")
    roles = relationship("Role", back_populates="organization")
    invitations = relationship("Invitation", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization {self.name}>"

# apps/team-hub/src/models/role.py

class Role(Base):
    __tablename__ = "roles"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: f"role_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Role information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, default=list)  # List of permission strings
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.name}>"

# apps/team-hub/src/models/invitation.py

class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"

class Invitation(Base):
    __tablename__ = "invitations"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Invitation details
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    invited_by_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Status and expiration
    status = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="invitations")
    invited_by = relationship("User", foreign_keys=[invited_by_id])
    
    def __repr__(self):
        return f"<Invitation {self.email} to {self.organization.name}>"
