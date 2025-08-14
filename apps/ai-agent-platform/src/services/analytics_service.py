"""
Analytics Service
Handles analytics and metrics for AI agents
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for agent analytics and metrics"""
    
    def __init__(self):
        # In-memory storage for demo (replace with analytics database in production)
        self.usage_data: Dict[str, List[Dict]] = defaultdict(list)
        self.performance_data: Dict[str, Dict] = defaultdict(dict)
        
    async def get_usage_analytics(self) -> Dict[str, Any]:
        """Get overall usage analytics"""
        total_agents = len(self.usage_data)
        total_calls = sum(len(calls) for calls in self.usage_data.values())
        
        # Calculate daily usage for the last 30 days
        daily_usage = defaultdict(int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        for agent_id, calls in self.usage_data.items():
            for call in calls:
                call_date = call.get("timestamp", datetime.utcnow())
                if isinstance(call_date, str):
                    call_date = datetime.fromisoformat(call_date.replace('Z', '+00:00'))
                
                if start_date <= call_date <= end_date:
                    date_key = call_date.strftime("%Y-%m-%d")
                    daily_usage[date_key] += 1
        
        # Get top performing agents
        agent_usage = []
        for agent_id, calls in self.usage_data.items():
            recent_calls = [
                call for call in calls 
                if datetime.fromisoformat(call.get("timestamp", "").replace('Z', '+00:00')) >= start_date
            ]
            
            if recent_calls:
                success_rate = sum(1 for call in recent_calls if call.get("success", True)) / len(recent_calls)
                avg_duration = sum(call.get("duration", 0) for call in recent_calls) / len(recent_calls)
                
                agent_usage.append({
                    "agent_id": agent_id,
                    "total_calls": len(recent_calls),
                    "success_rate": round(success_rate * 100, 1),
                    "average_duration": round(avg_duration, 2)
                })
        
        agent_usage.sort(key=lambda x: x["total_calls"], reverse=True)
        
        return {
            "total_agents": total_agents,
            "total_calls": total_calls,
            "daily_usage": dict(daily_usage),
            "top_agents": agent_usage[:10],
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    async def get_performance_analytics(self) -> Dict[str, Any]:
        """Get performance analytics"""
        performance_summary = {
            "overall_success_rate": 0.0,
            "average_response_time": 0.0,
            "total_interactions": 0,
            "satisfaction_scores": [],
            "performance_by_type": {},
            "trends": {}
        }
        
        all_calls = []
        for calls in self.usage_data.values():
            all_calls.extend(calls)
        
        if all_calls:
            # Overall metrics
            successful_calls = sum(1 for call in all_calls if call.get("success", True))
            performance_summary["overall_success_rate"] = round((successful_calls / len(all_calls)) * 100, 1)
            performance_summary["total_interactions"] = len(all_calls)
            
            # Average response time
            response_times = [call.get("response_time", 0) for call in all_calls if call.get("response_time")]
            if response_times:
                performance_summary["average_response_time"] = round(sum(response_times) / len(response_times), 2)
            
            # Satisfaction scores
            satisfaction_scores = [call.get("satisfaction", 0) for call in all_calls if call.get("satisfaction")]
            performance_summary["satisfaction_scores"] = satisfaction_scores
            
            # Performance by agent type
            type_performance = defaultdict(lambda: {"calls": 0, "success": 0, "avg_duration": 0})
            
            for call in all_calls:
                agent_type = call.get("agent_type", "unknown")
                type_performance[agent_type]["calls"] += 1
                if call.get("success", True):
                    type_performance[agent_type]["success"] += 1
                type_performance[agent_type]["avg_duration"] += call.get("duration", 0)
            
            for agent_type, data in type_performance.items():
                if data["calls"] > 0:
                    success_rate = (data["success"] / data["calls"]) * 100
                    avg_duration = data["avg_duration"] / data["calls"]
                    performance_summary["performance_by_type"][agent_type] = {
                        "success_rate": round(success_rate, 1),
                        "average_duration": round(avg_duration, 2),
                        "total_calls": data["calls"]
                    }
        
        return performance_summary
    
    async def record_agent_usage(self, agent_id: str, usage_data: Dict[str, Any]) -> bool:
        """Record usage data for an agent"""
        usage_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "success": usage_data.get("success", True),
            "duration": usage_data.get("duration", 0),
            "response_time": usage_data.get("response_time", 0),
            "satisfaction": usage_data.get("satisfaction"),
            "agent_type": usage_data.get("agent_type", "unknown"),
            "metadata": usage_data.get("metadata", {})
        }
        
        self.usage_data[agent_id].append(usage_record)
        logger.debug(f"Recorded usage for agent: {agent_id}")
        return True
    
    async def get_agent_analytics(self, agent_id: str) -> Dict[str, Any]:
        """Get analytics for a specific agent"""
        if agent_id not in self.usage_data:
            return {
                "agent_id": agent_id,
                "total_calls": 0,
                "success_rate": 0,
                "average_duration": 0,
                "satisfaction_score": 0,
                "usage_trend": {}
            }
        
        calls = self.usage_data[agent_id]
        
        # Basic metrics
        total_calls = len(calls)
        successful_calls = sum(1 for call in calls if call.get("success", True))
        success_rate = (successful_calls / total_calls) * 100 if total_calls > 0 else 0
        
        # Average duration
        durations = [call.get("duration", 0) for call in calls]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Satisfaction score
        satisfaction_scores = [call.get("satisfaction", 0) for call in calls if call.get("satisfaction")]
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
        
        # Usage trend (last 7 days)
        usage_trend = defaultdict(int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        for call in calls:
            call_date = datetime.fromisoformat(call.get("timestamp", "").replace('Z', '+00:00'))
            if start_date <= call_date <= end_date:
                date_key = call_date.strftime("%Y-%m-%d")
                usage_trend[date_key] += 1
        
        return {
            "agent_id": agent_id,
            "total_calls": total_calls,
            "success_rate": round(success_rate, 1),
            "average_duration": round(avg_duration, 2),
            "satisfaction_score": round(avg_satisfaction, 1),
            "usage_trend": dict(usage_trend),
            "last_used": calls[-1].get("timestamp") if calls else None
        }
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        current_time = datetime.utcnow()
        last_hour = current_time - timedelta(hours=1)
        
        recent_calls = []
        for calls in self.usage_data.values():
            for call in calls:
                call_time = datetime.fromisoformat(call.get("timestamp", "").replace('Z', '+00:00'))
                if call_time >= last_hour:
                    recent_calls.append(call)
        
        active_agents = len(set(call.get("agent_id") for call in recent_calls))
        calls_per_minute = len(recent_calls) / 60 if recent_calls else 0
        
        return {
            "timestamp": current_time.isoformat(),
            "active_agents": active_agents,
            "calls_last_hour": len(recent_calls),
            "calls_per_minute": round(calls_per_minute, 2),
            "system_status": "healthy" if calls_per_minute > 0 else "idle"
        }
