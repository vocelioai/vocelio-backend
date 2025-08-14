"""
Enhanced Agent Management Service - Merged from ai-agent-platform
Advanced agent lifecycle management, capabilities, and configuration
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)

class AgentStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    TRAINING = "training"
    TESTING = "testing"
    DEPLOYED = "deployed"
    MAINTENANCE = "maintenance"
    ARCHIVED = "archived"

class CapabilityType(str, Enum):
    CONVERSATION = "conversation"
    TASK_AUTOMATION = "task_automation"
    DATA_ANALYSIS = "data_analysis"
    INTEGRATION = "integration"
    WORKFLOW = "workflow"
    MONITORING = "monitoring"

class DeploymentEnvironment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class EnhancedAgentManagementService:
    """Enhanced agent management with advanced lifecycle and capabilities"""
    
    def __init__(self):
        # Agent storage with enhanced metadata
        self.agents: Dict[str, dict] = {}
        self.agent_capabilities: Dict[str, Set[str]] = {}
        self.agent_configurations: Dict[str, dict] = {}
        self.deployment_history: Dict[str, List[dict]] = {}
        self.performance_metrics: Dict[str, dict] = {}
        self.capability_definitions = self._initialize_capabilities()
        self.templates: Dict[str, dict] = self._initialize_templates()
        
    def _initialize_capabilities(self) -> Dict[str, dict]:
        """Initialize available agent capabilities"""
        return {
            # Conversation Capabilities
            "natural_language_processing": {
                "name": "Natural Language Processing",
                "type": CapabilityType.CONVERSATION,
                "description": "Advanced NLP for understanding and generating human language",
                "required_models": ["language_model"],
                "configuration": {
                    "supported_languages": ["en", "es", "fr", "de"],
                    "context_window": 4096,
                    "temperature": 0.7
                }
            },
            "sentiment_analysis": {
                "name": "Sentiment Analysis", 
                "type": CapabilityType.CONVERSATION,
                "description": "Analyze emotional tone and sentiment in conversations",
                "required_models": ["sentiment_model"],
                "configuration": {
                    "confidence_threshold": 0.8,
                    "supported_emotions": ["positive", "negative", "neutral", "angry", "happy", "sad"]
                }
            },
            "intent_recognition": {
                "name": "Intent Recognition",
                "type": CapabilityType.CONVERSATION, 
                "description": "Identify user intentions from natural language input",
                "required_models": ["intent_classifier"],
                "configuration": {
                    "custom_intents": [],
                    "fallback_threshold": 0.6
                }
            },
            
            # Task Automation Capabilities
            "appointment_scheduling": {
                "name": "Appointment Scheduling",
                "type": CapabilityType.TASK_AUTOMATION,
                "description": "Automated scheduling and calendar management",
                "required_models": [],
                "configuration": {
                    "calendar_integration": "google_calendar",
                    "booking_window_days": 30,
                    "time_zones": ["UTC", "EST", "PST"]
                }
            },
            "lead_qualification": {
                "name": "Lead Qualification",
                "type": CapabilityType.TASK_AUTOMATION,
                "description": "Qualify and score potential sales leads",
                "required_models": ["scoring_model"],
                "configuration": {
                    "qualification_criteria": ["budget", "authority", "need", "timeline"],
                    "scoring_weights": {"budget": 0.3, "authority": 0.2, "need": 0.3, "timeline": 0.2}
                }
            },
            "document_processing": {
                "name": "Document Processing",
                "type": CapabilityType.TASK_AUTOMATION,
                "description": "Extract and process information from documents",
                "required_models": ["document_ai"],
                "configuration": {
                    "supported_formats": ["pdf", "docx", "txt", "csv"],
                    "extraction_types": ["text", "tables", "forms", "signatures"]
                }
            },
            
            # Data Analysis Capabilities  
            "analytics_reporting": {
                "name": "Analytics & Reporting",
                "type": CapabilityType.DATA_ANALYSIS,
                "description": "Generate insights and reports from data",
                "required_models": ["analytics_model"],
                "configuration": {
                    "report_types": ["performance", "trends", "forecasts"],
                    "visualization_formats": ["charts", "graphs", "tables"]
                }
            },
            "predictive_modeling": {
                "name": "Predictive Modeling",
                "type": CapabilityType.DATA_ANALYSIS,
                "description": "Create predictive models from historical data",
                "required_models": ["ml_pipeline"],
                "configuration": {
                    "model_types": ["regression", "classification", "clustering"],
                    "validation_methods": ["cross_validation", "holdout"]
                }
            },
            
            # Integration Capabilities
            "crm_integration": {
                "name": "CRM Integration",
                "type": CapabilityType.INTEGRATION,
                "description": "Connect with Customer Relationship Management systems",
                "required_models": [],
                "configuration": {
                    "supported_crms": ["salesforce", "hubspot", "pipedrive"],
                    "sync_frequency": "real_time",
                    "data_mapping": {}
                }
            },
            "api_connectivity": {
                "name": "API Connectivity", 
                "type": CapabilityType.INTEGRATION,
                "description": "Connect to external APIs and services",
                "required_models": [],
                "configuration": {
                    "authentication_methods": ["api_key", "oauth", "basic_auth"],
                    "rate_limiting": {"requests_per_minute": 60},
                    "retry_policy": {"max_retries": 3, "backoff": "exponential"}
                }
            },
            
            # Workflow Capabilities
            "workflow_automation": {
                "name": "Workflow Automation",
                "type": CapabilityType.WORKFLOW,
                "description": "Automate business workflows and processes",
                "required_models": [],
                "configuration": {
                    "trigger_types": ["schedule", "event", "manual"],
                    "action_types": ["email", "sms", "api_call", "data_update"],
                    "conditions": ["if_then", "loops", "branches"]
                }
            },
            
            # Monitoring Capabilities
            "performance_monitoring": {
                "name": "Performance Monitoring",
                "type": CapabilityType.MONITORING,
                "description": "Monitor agent performance and system health",
                "required_models": [],
                "configuration": {
                    "metrics": ["response_time", "accuracy", "user_satisfaction"],
                    "alerts": {"thresholds": {}, "notification_channels": []},
                    "reporting_frequency": "daily"
                }
            }
        }

    def _initialize_templates(self) -> Dict[str, dict]:
        """Initialize agent templates for quick deployment"""
        return {
            "sales_assistant": {
                "name": "Sales Assistant Template",
                "description": "Pre-configured agent for sales and lead generation",
                "capabilities": ["natural_language_processing", "intent_recognition", "lead_qualification", "crm_integration", "appointment_scheduling"],
                "industry": "sales",
                "configuration": {
                    "personality": "professional_friendly",
                    "conversation_style": "consultative",
                    "lead_scoring_enabled": True,
                    "follow_up_automation": True
                }
            },
            "customer_support": {
                "name": "Customer Support Template",
                "description": "Intelligent customer service agent",
                "capabilities": ["natural_language_processing", "sentiment_analysis", "intent_recognition", "document_processing", "api_connectivity"],
                "industry": "support",
                "configuration": {
                    "personality": "helpful_empathetic",
                    "escalation_rules": {"sentiment_threshold": -0.5, "complexity_threshold": 0.8},
                    "knowledge_base_integration": True,
                    "ticket_creation": True
                }
            },
            "healthcare_scheduler": {
                "name": "Healthcare Scheduler Template", 
                "description": "HIPAA-compliant medical appointment scheduling",
                "capabilities": ["natural_language_processing", "appointment_scheduling", "document_processing", "performance_monitoring"],
                "industry": "healthcare",
                "configuration": {
                    "personality": "professional_caring",
                    "hipaa_compliance": True,
                    "insurance_verification": True,
                    "reminder_system": True,
                    "privacy_level": "high"
                }
            },
            "data_analyst": {
                "name": "Data Analyst Template",
                "description": "AI agent for data analysis and reporting",
                "capabilities": ["analytics_reporting", "predictive_modeling", "document_processing", "api_connectivity"],
                "industry": "analytics", 
                "configuration": {
                    "personality": "analytical_precise",
                    "report_automation": True,
                    "data_visualization": True,
                    "scheduled_reports": True
                }
            }
        }

    async def create_enhanced_agent(
        self,
        user_id: str,
        agent_data: dict,
        capabilities: List[str] = None,
        template_id: Optional[str] = None
    ) -> dict:
        """Create an agent with enhanced capabilities and configuration"""
        
        agent_id = str(uuid.uuid4())
        
        # Start with template if provided
        if template_id and template_id in self.templates:
            template = self.templates[template_id]
            base_config = template["configuration"].copy()
            base_capabilities = template["capabilities"].copy()
            industry = template.get("industry", "general")
        else:
            base_config = {}
            base_capabilities = []
            industry = agent_data.get("industry", "general")
        
        # Merge with provided data
        agent_capabilities = list(set(base_capabilities + (capabilities or [])))
        
        # Validate capabilities
        valid_capabilities = []
        for cap in agent_capabilities:
            if cap in self.capability_definitions:
                valid_capabilities.append(cap)
            else:
                logger.warning(f"Unknown capability: {cap}")
        
        enhanced_agent = {
            "id": agent_id,
            "user_id": user_id,
            "name": agent_data.get("name", f"Agent {agent_id[:8]}"),
            "description": agent_data.get("description", "Enhanced AI agent"),
            "status": AgentStatus.INACTIVE,
            "industry": industry,
            "template_id": template_id,
            "capabilities": valid_capabilities,
            "version": "1.0.0",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_deployed": None,
            "deployment_environment": None,
            "performance_score": 0.0,
            "usage_stats": {
                "total_conversations": 0,
                "total_tasks_completed": 0,
                "average_response_time": 0.0,
                "user_satisfaction_score": 0.0,
                "uptime_percentage": 100.0
            },
            "configuration": {**base_config, **agent_data.get("configuration", {})},
            "metadata": agent_data.get("metadata", {})
        }
        
        # Store agent and initialize related data
        self.agents[agent_id] = enhanced_agent
        self.agent_capabilities[agent_id] = set(valid_capabilities)
        self.agent_configurations[agent_id] = enhanced_agent["configuration"]
        self.deployment_history[agent_id] = []
        self.performance_metrics[agent_id] = {
            "daily_metrics": {},
            "weekly_metrics": {},
            "monthly_metrics": {},
            "alerts": []
        }
        
        logger.info(f"Enhanced agent created: {agent_id} with capabilities: {valid_capabilities}")
        
        return {
            "agent_id": agent_id,
            "status": "created",
            "capabilities_configured": len(valid_capabilities),
            "deployment_ready": len(valid_capabilities) > 0,
            "management_url": f"/agents/{agent_id}/manage"
        }

    async def configure_agent_capabilities(
        self, 
        agent_id: str, 
        capability_configs: Dict[str, dict]
    ) -> dict:
        """Configure specific capabilities for an agent"""
        
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        configured_capabilities = []
        
        for capability_id, config in capability_configs.items():
            if capability_id not in self.capability_definitions:
                logger.warning(f"Unknown capability: {capability_id}")
                continue
            
            capability_def = self.capability_definitions[capability_id]
            
            # Merge with default configuration
            full_config = capability_def["configuration"].copy()
            full_config.update(config)
            
            # Store capability configuration
            if agent_id not in self.agent_configurations:
                self.agent_configurations[agent_id] = {}
            
            self.agent_configurations[agent_id][capability_id] = full_config
            
            # Add to agent capabilities
            self.agent_capabilities[agent_id].add(capability_id)
            configured_capabilities.append(capability_id)
        
        # Update agent record
        agent["capabilities"] = list(self.agent_capabilities[agent_id])
        agent["updated_at"] = datetime.utcnow()
        
        logger.info(f"Configured capabilities for agent {agent_id}: {configured_capabilities}")
        
        return {
            "agent_id": agent_id,
            "configured_capabilities": configured_capabilities,
            "total_capabilities": len(agent["capabilities"]),
            "status": "configured"
        }

    async def deploy_agent(
        self, 
        agent_id: str, 
        environment: DeploymentEnvironment,
        deployment_config: Optional[dict] = None
    ) -> dict:
        """Deploy an agent to a specific environment"""
        
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        if not agent["capabilities"]:
            raise ValueError("Agent must have at least one capability configured")
        
        deployment_id = str(uuid.uuid4())
        deployment_time = datetime.utcnow()
        
        # Validate capability requirements
        missing_models = []
        for capability_id in agent["capabilities"]:
            capability_def = self.capability_definitions[capability_id]
            for model in capability_def.get("required_models", []):
                # In production, check if models are available
                pass
        
        if missing_models:
            raise ValueError(f"Missing required models: {missing_models}")
        
        deployment_record = {
            "id": deployment_id,
            "agent_id": agent_id,
            "environment": environment.value,
            "version": agent["version"],
            "deployed_at": deployment_time,
            "deployed_by": agent["user_id"],
            "status": "active",
            "configuration_snapshot": self.agent_configurations.get(agent_id, {}),
            "capabilities_snapshot": list(agent["capabilities"]),
            "endpoint_url": f"/agents/{agent_id}/chat",
            "health_check_url": f"/agents/{agent_id}/health",
            "metrics_url": f"/agents/{agent_id}/metrics"
        }
        
        # Update agent status
        agent["status"] = AgentStatus.DEPLOYED
        agent["deployment_environment"] = environment.value
        agent["last_deployed"] = deployment_time
        agent["updated_at"] = deployment_time
        
        # Record deployment history
        if agent_id not in self.deployment_history:
            self.deployment_history[agent_id] = []
        self.deployment_history[agent_id].append(deployment_record)
        
        logger.info(f"Agent deployed: {agent_id} to {environment.value}")
        
        return {
            "deployment_id": deployment_id,
            "agent_id": agent_id,
            "environment": environment.value,
            "status": "deployed",
            "endpoint_url": deployment_record["endpoint_url"],
            "health_check_url": deployment_record["health_check_url"],
            "deployed_at": deployment_time.isoformat()
        }

    async def get_agent_analytics(
        self, 
        agent_id: str, 
        time_range: str = "7d",
        metrics: List[str] = None
    ) -> dict:
        """Get comprehensive analytics for an agent"""
        
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        # Default metrics if none specified
        if not metrics:
            metrics = ["conversations", "response_time", "satisfaction", "errors", "uptime"]
        
        # Generate analytics data (in production, query from time-series database)
        analytics_data = {
            "agent_id": agent_id,
            "time_range": time_range,
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": {}
        }
        
        # Simulate metrics data
        if "conversations" in metrics:
            analytics_data["metrics"]["conversations"] = {
                "total": agent["usage_stats"]["total_conversations"],
                "daily_average": agent["usage_stats"]["total_conversations"] / 30,
                "trend": "+15%",
                "peak_hour": "14:00",
                "success_rate": 94.5
            }
        
        if "response_time" in metrics:
            analytics_data["metrics"]["response_time"] = {
                "average_ms": agent["usage_stats"]["average_response_time"] * 1000,
                "p95_ms": agent["usage_stats"]["average_response_time"] * 1200,
                "p99_ms": agent["usage_stats"]["average_response_time"] * 1500,
                "trend": "-8%"
            }
        
        if "satisfaction" in metrics:
            analytics_data["metrics"]["satisfaction"] = {
                "average_score": agent["usage_stats"]["user_satisfaction_score"],
                "total_ratings": 142,
                "distribution": {"5_star": 65, "4_star": 45, "3_star": 20, "2_star": 8, "1_star": 4},
                "trend": "+3%"
            }
        
        if "errors" in metrics:
            analytics_data["metrics"]["errors"] = {
                "total_errors": 12,
                "error_rate": 0.8,
                "common_errors": ["timeout", "capability_not_found", "configuration_error"],
                "trend": "-25%"
            }
        
        if "uptime" in metrics:
            analytics_data["metrics"]["uptime"] = {
                "percentage": agent["usage_stats"]["uptime_percentage"],
                "downtime_minutes": 43.2,
                "incidents": 2,
                "trend": "+2%"
            }
        
        # Capability-specific metrics
        capability_metrics = {}
        for capability_id in agent["capabilities"]:
            capability_def = self.capability_definitions[capability_id]
            capability_metrics[capability_id] = {
                "usage_frequency": f"{capability_id}_used_daily",
                "success_rate": 96.2,
                "average_execution_time": 1.2
            }
        
        analytics_data["capability_metrics"] = capability_metrics
        
        return analytics_data

    async def update_agent_configuration(
        self, 
        agent_id: str, 
        configuration_updates: dict
    ) -> dict:
        """Update agent configuration with validation"""
        
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        # Backup current configuration
        backup_config = self.agent_configurations.get(agent_id, {}).copy()
        
        try:
            # Update configuration
            current_config = self.agent_configurations.get(agent_id, {})
            
            for key, value in configuration_updates.items():
                if key in agent["capabilities"]:
                    # Capability-specific configuration
                    if key not in current_config:
                        current_config[key] = {}
                    current_config[key].update(value if isinstance(value, dict) else {key: value})
                else:
                    # General configuration
                    current_config[key] = value
            
            self.agent_configurations[agent_id] = current_config
            agent["configuration"] = current_config
            agent["updated_at"] = datetime.utcnow()
            
            # If agent is deployed, may need redeployment
            redeploy_required = agent["status"] == AgentStatus.DEPLOYED
            
            logger.info(f"Configuration updated for agent {agent_id}")
            
            return {
                "agent_id": agent_id,
                "status": "updated",
                "redeploy_required": redeploy_required,
                "backup_available": True,
                "updated_at": agent["updated_at"].isoformat()
            }
            
        except Exception as e:
            # Restore backup on error
            self.agent_configurations[agent_id] = backup_config
            agent["configuration"] = backup_config
            logger.error(f"Configuration update failed for agent {agent_id}: {str(e)}")
            raise ValueError(f"Configuration update failed: {str(e)}")

    async def get_capability_catalog(self, category: Optional[str] = None) -> dict:
        """Get catalog of available capabilities"""
        
        capabilities = []
        
        for cap_id, cap_def in self.capability_definitions.items():
            if category and cap_def["type"].value != category:
                continue
            
            capability_info = {
                "id": cap_id,
                "name": cap_def["name"],
                "type": cap_def["type"].value,
                "description": cap_def["description"],
                "required_models": cap_def.get("required_models", []),
                "configuration_options": list(cap_def.get("configuration", {}).keys()),
                "compatible_industries": self._get_compatible_industries(cap_id)
            }
            capabilities.append(capability_info)
        
        return {
            "total_capabilities": len(capabilities),
            "categories": [t.value for t in CapabilityType],
            "capabilities": capabilities
        }

    def _get_compatible_industries(self, capability_id: str) -> List[str]:
        """Get industries compatible with a capability"""
        # Industry compatibility mapping
        industry_mapping = {
            "natural_language_processing": ["sales", "support", "healthcare", "education", "general"],
            "appointment_scheduling": ["healthcare", "services", "consulting"],
            "lead_qualification": ["sales", "marketing", "real_estate"],
            "crm_integration": ["sales", "marketing", "services"],
            "sentiment_analysis": ["support", "marketing", "social_media"],
            "analytics_reporting": ["analytics", "finance", "operations", "general"],
            "document_processing": ["healthcare", "legal", "finance", "hr"]
        }
        
        return industry_mapping.get(capability_id, ["general"])

    async def clone_agent(self, agent_id: str, new_name: str, user_id: str) -> dict:
        """Clone an existing agent with all configurations"""
        
        source_agent = self.agents.get(agent_id)
        if not source_agent:
            raise ValueError("Source agent not found")
        
        # Create clone data
        clone_data = {
            "name": new_name,
            "description": f"Clone of {source_agent['name']}",
            "industry": source_agent["industry"],
            "configuration": source_agent["configuration"].copy(),
            "metadata": {"cloned_from": agent_id, "cloned_at": datetime.utcnow().isoformat()}
        }
        
        # Create the cloned agent
        clone_result = await self.create_enhanced_agent(
            user_id=user_id,
            agent_data=clone_data,
            capabilities=source_agent["capabilities"].copy(),
            template_id=source_agent.get("template_id")
        )
        
        clone_id = clone_result["agent_id"]
        
        # Copy capability configurations
        if agent_id in self.agent_configurations:
            self.agent_configurations[clone_id] = self.agent_configurations[agent_id].copy()
        
        logger.info(f"Agent cloned: {agent_id} -> {clone_id}")
        
        return {
            "clone_id": clone_id,
            "source_id": agent_id,
            "status": "cloned",
            "capabilities_copied": len(source_agent["capabilities"]),
            "ready_for_deployment": True
        }

    async def get_agent_health(self, agent_id: str) -> dict:
        """Get health status and diagnostics for an agent"""
        
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        # Perform health checks
        health_status = {
            "agent_id": agent_id,
            "status": agent["status"],
            "overall_health": "healthy",
            "last_check": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # Check capability health
        for capability_id in agent["capabilities"]:
            capability_def = self.capability_definitions[capability_id]
            
            # Simulate capability health check
            health_status["checks"][capability_id] = {
                "status": "healthy",
                "response_time_ms": 150,
                "last_error": None,
                "error_rate_24h": 0.2
            }
        
        # Check deployment health
        if agent["status"] == AgentStatus.DEPLOYED:
            health_status["checks"]["deployment"] = {
                "status": "healthy",
                "environment": agent["deployment_environment"],
                "uptime_hours": 168.5,
                "last_restart": None
            }
        
        # Check configuration health
        health_status["checks"]["configuration"] = {
            "status": "healthy",
            "last_updated": agent["updated_at"].isoformat(),
            "validation_errors": []
        }
        
        return health_status
