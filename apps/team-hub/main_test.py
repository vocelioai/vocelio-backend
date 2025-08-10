#!/usr/bin/env python3
"""
👥 Vocelio.ai Team Hub Service - Test Version
Simplified version for testing without database dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import random
import uvicorn

# Pydantic Models
class TeamMember(BaseModel):
    """Team member model"""
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role")
    department: str = Field(..., description="Department")
    status: str = Field(..., description="User status")
    permissions: List[str] = Field(..., description="User permissions")
    last_active: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

class TeamStats(BaseModel):
    """Team statistics"""
    total_members: int = Field(..., description="Total team members")
    active_members: int = Field(..., description="Active members")
    departments: int = Field(..., description="Number of departments")
    roles: int = Field(..., description="Number of roles")
    online_now: int = Field(..., description="Members online now")

class InviteRequest(BaseModel):
    """Invite new team member request"""
    email: str = Field(..., description="Email to invite")
    role: str = Field(..., description="Role to assign")
    department: str = Field(..., description="Department to assign")
    permissions: List[str] = Field(["read"], description="Permissions to grant")

# FastAPI app
app = FastAPI(
    title="👥 Vocelio.ai Team Hub Service (Test)",
    description="Team management and collaboration platform - Test Version",
    version="1.0.0-test"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
MOCK_TEAM_MEMBERS = [
    {
        "user_id": "user_001",
        "name": "Alice Johnson",
        "email": "alice@vocelio.ai",
        "role": "Admin",
        "department": "Engineering",
        "status": "active",
        "permissions": ["read", "write", "admin"],
        "last_active": datetime.now(),
        "created_at": datetime.now()
    },
    {
        "user_id": "user_002",
        "name": "Bob Smith",
        "email": "bob@vocelio.ai",
        "role": "Manager",
        "department": "Sales",
        "status": "active",
        "permissions": ["read", "write"],
        "last_active": datetime.now(),
        "created_at": datetime.now()
    },
    {
        "user_id": "user_003",
        "name": "Carol Davis",
        "email": "carol@vocelio.ai",
        "role": "Developer",
        "department": "Engineering",
        "status": "active",
        "permissions": ["read", "write"],
        "last_active": datetime.now(),
        "created_at": datetime.now()
    }
]

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Vocelio.ai Team Hub Service",
        "version": "1.0.0-test",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "team-hub",
        "status": "healthy",
        "version": "1.0.0-test",
        "timestamp": datetime.now().isoformat(),
        "database_connected": True,  # Mock
        "auth_service_connected": True  # Mock
    }

@app.get("/api/v1/team/members", response_model=List[TeamMember])
async def get_team_members(
    department: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None
):
    """Get all team members with optional filtering"""
    members = MOCK_TEAM_MEMBERS.copy()
    
    if department:
        members = [m for m in members if m["department"].lower() == department.lower()]
    if role:
        members = [m for m in members if m["role"].lower() == role.lower()]
    if status:
        members = [m for m in members if m["status"] == status]
    
    return members

@app.get("/api/v1/team/members/{user_id}")
async def get_team_member(user_id: str):
    """Get specific team member details"""
    for member in MOCK_TEAM_MEMBERS:
        if member["user_id"] == user_id:
            return member
    
    raise HTTPException(status_code=404, detail="Team member not found")

@app.post("/api/v1/team/invite", response_model=dict)
async def invite_team_member(invite_request: InviteRequest):
    """Invite a new team member"""
    # Generate new user ID
    new_user_id = f"user_{random.randint(1000, 9999):03d}"
    
    new_member = {
        "user_id": new_user_id,
        "name": invite_request.email.split('@')[0].title(),
        "email": invite_request.email,
        "role": invite_request.role,
        "department": invite_request.department,
        "status": "invited",
        "permissions": invite_request.permissions,
        "last_active": datetime.now(),
        "created_at": datetime.now()
    }
    
    MOCK_TEAM_MEMBERS.append(new_member)
    
    return {
        "message": f"Invitation sent to {invite_request.email}",
        "user_id": new_user_id,
        "status": "invited"
    }

@app.delete("/api/v1/team/members/{user_id}")
async def remove_team_member(user_id: str):
    """Remove a team member"""
    for i, member in enumerate(MOCK_TEAM_MEMBERS):
        if member["user_id"] == user_id:
            removed_member = MOCK_TEAM_MEMBERS.pop(i)
            return {"message": f"Team member {removed_member['name']} removed successfully"}
    
    raise HTTPException(status_code=404, detail="Team member not found")

@app.get("/api/v1/team/stats", response_model=TeamStats)
async def get_team_stats():
    """Get team statistics"""
    active_members = [m for m in MOCK_TEAM_MEMBERS if m["status"] == "active"]
    departments = len(set(m["department"] for m in MOCK_TEAM_MEMBERS))
    roles = len(set(m["role"] for m in MOCK_TEAM_MEMBERS))
    
    return TeamStats(
        total_members=len(MOCK_TEAM_MEMBERS),
        active_members=len(active_members),
        departments=departments,
        roles=roles,
        online_now=random.randint(1, len(active_members))
    )

@app.get("/api/v1/team/departments")
async def get_departments():
    """Get list of departments"""
    departments = list(set(m["department"] for m in MOCK_TEAM_MEMBERS))
    return {
        "departments": [
            {"name": dept, "member_count": len([m for m in MOCK_TEAM_MEMBERS if m["department"] == dept])}
            for dept in departments
        ]
    }

@app.get("/api/v1/team/roles")
async def get_roles():
    """Get list of roles"""
    roles = list(set(m["role"] for m in MOCK_TEAM_MEMBERS))
    return {
        "roles": [
            {"name": role, "member_count": len([m for m in MOCK_TEAM_MEMBERS if m["role"] == role])}
            for role in roles
        ]
    }

@app.put("/api/v1/team/members/{user_id}/permissions")
async def update_permissions(user_id: str, permissions: List[str]):
    """Update team member permissions"""
    for member in MOCK_TEAM_MEMBERS:
        if member["user_id"] == user_id:
            member["permissions"] = permissions
            return {"message": f"Permissions updated for {member['name']}", "permissions": permissions}
    
    raise HTTPException(status_code=404, detail="Team member not found")

# Run server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
