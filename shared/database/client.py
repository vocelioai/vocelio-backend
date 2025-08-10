# shared/database/client.py
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import json

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Enhanced Supabase client with connection pooling and error handling"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.client: Optional[Client] = None
        self._initialized = False
        
        if not self.url or not self.key:
            logger.warning("⚠️ Supabase credentials not found - database features will be limited")
            return
        
        # Configure client options for production
        options = ClientOptions()
        options.auto_refresh_token = True
        options.persist_session = True
        
        try:
            self.client = create_client(self.url, self.key, options)
            logger.info("✅ Supabase client initialized")
            self._initialized = True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
    
    def is_connected(self) -> bool:
        """Check if client is properly initialized"""
        return self._initialized and self.client is not None
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        if not self.is_connected():
            return False
        
        try:
            # Simple query to test connection
            result = self.client.table("organizations").select("id").limit(1).execute()
            logger.info("✅ Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False
    
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        if not self.is_connected():
            raise RuntimeError("Supabase client not initialized")
        return self.client

# Global Supabase client instance
supabase_client = SupabaseClient()
supabase = supabase_client.get_client() if supabase_client.is_connected() else None

# Database utility functions
class DatabaseUtils:
    """Utility functions for database operations"""
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Format datetime for database storage"""
        return dt.isoformat()
    
    @staticmethod
    def safe_json_decode(json_str: str) -> Dict[Any, Any]:
        """Safely decode JSON string"""
        try:
            return json.loads(json_str) if json_str else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @staticmethod
    def safe_json_encode(data: Any) -> str:
        """Safely encode data to JSON string"""
        try:
            return json.dumps(data) if data is not None else "{}"
        except (TypeError, ValueError):
            return "{}"
    
    @staticmethod
    def build_filter_query(table_name: str, filters: Dict[str, Any]):
        """Build filtered query for Supabase"""
        if not supabase:
            raise RuntimeError("Database not available")
        
        query = supabase.table(table_name).select("*")
        
        for key, value in filters.items():
            if value is not None:
                if isinstance(value, list):
                    query = query.in_(key, value)
                elif isinstance(value, dict):
                    # Handle range queries
                    if "gte" in value:
                        query = query.gte(key, value["gte"])
                    if "lte" in value:
                        query = query.lte(key, value["lte"])
                    if "gt" in value:
                        query = query.gt(key, value["gt"])
                    if "lt" in value:
                        query = query.lt(key, value["lt"])
                else:
                    query = query.eq(key, value)
        
        return query

# Database Models Base Classes
class BaseRepository:
    """Base repository class for database operations"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        if not supabase:
            raise RuntimeError("Database not available")
        self.client = supabase
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record"""
        try:
            data["created_at"] = DatabaseUtils.format_datetime(datetime.utcnow())
            result = self.client.table(self.table_name).insert(data).execute()
            
            if result.data:
                logger.info(f"✅ Created record in {self.table_name}: {result.data[0].get('id')}")
                return result.data[0]
            else:
                raise Exception("No data returned from insert")
        except Exception as e:
            logger.error(f"❌ Error creating record in {self.table_name}: {e}")
            raise
    
    async def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        try:
            result = self.client.table(self.table_name).select("*").eq("id", record_id).execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Error getting record from {self.table_name}: {e}")
            return None
    
    async def update(self, record_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update record by ID"""
        try:
            data["updated_at"] = DatabaseUtils.format_datetime(datetime.utcnow())
            result = self.client.table(self.table_name).update(data).eq("id", record_id).execute()
            
            if result.data:
                logger.info(f"✅ Updated record in {self.table_name}: {record_id}")
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ Error updating record in {self.table_name}: {e}")
            raise
    
    async def delete(self, record_id: str) -> bool:
        """Delete record by ID"""
        try:
            result = self.client.table(self.table_name).delete().eq("id", record_id).execute()
            logger.info(f"✅ Deleted record from {self.table_name}: {record_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting record from {self.table_name}: {e}")
            return False
    
    async def soft_delete(self, record_id: str) -> bool:
        """Soft delete record by setting deleted_at"""
        try:
            data = {
                "deleted_at": DatabaseUtils.format_datetime(datetime.utcnow()),
                "updated_at": DatabaseUtils.format_datetime(datetime.utcnow())
            }
            result = self.client.table(self.table_name).update(data).eq("id", record_id).execute()
            logger.info(f"✅ Soft deleted record from {self.table_name}: {record_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error soft deleting record from {self.table_name}: {e}")
            return False
    
    async def list_records(
        self, 
        filters: Dict[str, Any] = None,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "created_at",
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """List records with filtering and pagination"""
        try:
            query = self.client.table(self.table_name).select("*")
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query = query.eq(key, value)
            
            # Exclude soft deleted records by default
            query = query.is_("deleted_at", "null")
            
            # Apply ordering
            query = query.order(order_by, desc=not ascending)
            
            # Apply pagination
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"❌ Error listing records from {self.table_name}: {e}")
            return []
    
    async def count_records(self, filters: Dict[str, Any] = None) -> int:
        """Count records with optional filtering"""
        try:
            query = self.client.table(self.table_name).select("id", count="exact")
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query = query.eq(key, value)
            
            # Exclude soft deleted records
            query = query.is_("deleted_at", "null")
            
            result = query.execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"❌ Error counting records in {self.table_name}: {e}")
            return 0
    
    async def exists(self, filters: Dict[str, Any]) -> bool:
        """Check if record exists with given filters"""
        count = await self.count_records(filters)
        return count > 0

# Specific Repository Classes
class OrganizationRepository(BaseRepository):
    """Repository for organization operations"""
    
    def __init__(self):
        super().__init__("organizations")
    
    async def get_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get organization by domain"""
        try:
            result = self.client.table(self.table_name).select("*").eq("domain", domain).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Error getting organization by domain: {e}")
            return None
    
    async def update_usage(self, org_id: str, usage_data: Dict[str, Any]) -> bool:
        """Update organization usage statistics"""
        try:
            current_usage = await self.get_by_id(org_id)
            if not current_usage:
                return False
            
            # Merge usage data
            updated_usage = current_usage.get("usage_stats", {})
            updated_usage.update(usage_data)
            
            await self.update(org_id, {"usage_stats": updated_usage})
            return True
        except Exception as e:
            logger.error(f"❌ Error updating organization usage: {e}")
            return False

class UserRepository(BaseRepository):
    """Repository for user operations"""
    
    def __init__(self):
        super().__init__("users")
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            result = self.client.table(self.table_name).select("*").eq("email", email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Error getting user by email: {e}")
            return None
    
    async def get_by_organization(self, org_id: str) -> List[Dict[str, Any]]:
        """Get all users in organization"""
        return await self.list_records({"organization_id": org_id})
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            await self.update(user_id, {"last_login": DatabaseUtils.format_datetime(datetime.utcnow())})
            return True
        except Exception as e:
            logger.error(f"❌ Error updating last login: {e}")
            return False

class AgentRepository(BaseRepository):
    """Repository for AI agent operations"""
    
    def __init__(self):
        super().__init__("agents")
    
    async def get_by_organization(self, org_id: str) -> List[Dict[str, Any]]:
        """Get all agents in organization"""
        return await self.list_records({"organization_id": org_id})
    
    async def get_active_agents(self, org_id: str) -> List[Dict[str, Any]]:
        """Get active agents in organization"""
        return await self.list_records({"organization_id": org_id, "status": "active"})
    
    async def update_usage_stats(self, agent_id: str, stats: Dict[str, Any]) -> bool:
        """Update agent usage statistics"""
        try:
            current_data = await self.get_by_id(agent_id)
            if not current_data:
                return False
            
            current_stats = current_data.get("usage_stats", {})
            current_stats.update(stats)
            
            await self.update(agent_id, {"usage_stats": current_stats})
            return True
        except Exception as e:
            logger.error(f"❌ Error updating agent usage stats: {e}")
            return False

class CampaignRepository(BaseRepository):
    """Repository for campaign operations"""
    
    def __init__(self):
        super().__init__("campaigns")
    
    async def get_active_campaigns(self, org_id: str) -> List[Dict[str, Any]]:
        """Get active campaigns"""
        return await self.list_records({"organization_id": org_id, "status": "active"})
    
    async def get_by_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get campaigns using specific agent"""
        return await self.list_records({"agent_id": agent_id})

class CallRepository(BaseRepository):
    """Repository for call operations"""
    
    def __init__(self):
        super().__init__("calls")
    
    async def get_by_campaign(self, campaign_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get calls for specific campaign"""
        return await self.list_records({"campaign_id": campaign_id}, limit=limit)
    
    async def get_recent_calls(self, org_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent calls for organization"""
        try:
            cutoff_time = datetime.utcnow().replace(hour=datetime.utcnow().hour - hours)
            cutoff_str = DatabaseUtils.format_datetime(cutoff_time)
            
            result = self.client.table(self.table_name).select("*").eq(
                "organization_id", org_id
            ).gte("created_at", cutoff_str).order("created_at", desc=True).execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"❌ Error getting recent calls: {e}")
            return []
    
    async def update_call_outcome(self, call_id: str, outcome: str, summary: str = None) -> bool:
        """Update call outcome and summary"""
        try:
            update_data = {
                "call_outcome": outcome,
                "status": "completed",
                "completed_at": DatabaseUtils.format_datetime(datetime.utcnow())
            }
            
            if summary:
                update_data["ai_summary"] = summary
            
            await self.update(call_id, update_data)
            return True
        except Exception as e:
            logger.error(f"❌ Error updating call outcome: {e}")
            return False

# Initialize repositories
org_repo = OrganizationRepository() if supabase else None
user_repo = UserRepository() if supabase else None
agent_repo = AgentRepository() if supabase else None
campaign_repo = CampaignRepository() if supabase else None
call_repo = CallRepository() if supabase else None

# Database health check
async def check_database_health() -> Dict[str, Any]:
    """Check database health and return status"""
    if not supabase_client.is_connected():
        return {
            "status": "unavailable",
            "message": "Database client not initialized",
            "timestamp": DatabaseUtils.format_datetime(datetime.utcnow())
        }
    
    try:
        connection_ok = await supabase_client.test_connection()
        
        if connection_ok:
            # Get basic stats
            stats = {}
            try:
                if org_repo:
                    stats["organizations"] = await org_repo.count_records()
                if user_repo:
                    stats["users"] = await user_repo.count_records()
                if agent_repo:
                    stats["agents"] = await agent_repo.count_records()
                if call_repo:
                    stats["calls"] = await call_repo.count_records()
            except:
                stats = {"error": "Could not fetch stats"}
            
            return {
                "status": "healthy",
                "message": "Database connection successful",
                "stats": stats,
                "timestamp": DatabaseUtils.format_datetime(datetime.utcnow())
            }
        else:
            return {
                "status": "unhealthy",
                "message": "Database connection failed",
                "timestamp": DatabaseUtils.format_datetime(datetime.utcnow())
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database health check failed: {str(e)}",
            "timestamp": DatabaseUtils.format_datetime(datetime.utcnow())
        }

# Export everything
__all__ = [
    "supabase",
    "supabase_client", 
    "DatabaseUtils",
    "BaseRepository",
    "OrganizationRepository",
    "UserRepository", 
    "AgentRepository",
    "CampaignRepository",
    "CallRepository",
    "org_repo",
    "user_repo",
    "agent_repo", 
    "campaign_repo",
    "call_repo",
    "check_database_health",
    "init_database",
    "get_database"
]

# Global database instance
_db_client = None

def init_database():
    """Initialize the global database client"""
    global _db_client
    _db_client = SupabaseClient()
    return _db_client

def get_database():
    """Get the global database client"""
    global _db_client
    if _db_client is None:
        _db_client = init_database()
    return _db_client