# apps/call-center/src/services/ai_service.py
from typing import Dict, Any, Optional, List
import logging
import json
import asyncio
from datetime import datetime
import openai
from anthropic import Anthropic
import httpx

from core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def analyze_call_real_time(self, call_id: str) -> Dict[str, Any]:
        """Analyze call in real-time and provide AI insights"""
        try:
            # Get call transcript and context
            call_context = await self._get_call_context(call_id)
            
            if not call_context.get('transcript'):
                return self._get_default_insights()
            
            # Analyze with AI
            analysis = await self._analyze_conversation(
                call_context['transcript'],
                call_context.get('customer_info', {}),
                call_context.get('campaign_info', {})
            )
            
            return {
                "conversion_probability": analysis.get('conversion_probability', 50.0),
                "next_best_action": analysis.get('next_best_action', 'Continue building rapport'),
                "objections": analysis.get('objections', []),
                "sentiment": analysis.get('sentiment', 0.5),
                "recommendations": analysis.get('recommendations', []),
                "confidence": analysis.get('confidence', 0.8)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing call {call_id}: {e}")
            return self._get_default_insights()
    
    async def generate_response(self, call_sid: str, customer_message: str, confidence: float) -> Dict[str, Any]:
        """Generate AI response for customer message"""
        try:
            # Get conversation context
            context = await self._get_conversation_context(call_sid)
            
            # Generate response using OpenAI
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_agent_system_prompt(context)
                    },
                    {
                        "role": "user", 
                        "content": f"Customer said: {customer_message}"
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Analyze response for next actions
            next_action = await self._determine_next_action(customer_message, ai_response)
            
            return {
                "text": ai_response,
                "continue_conversation": next_action.get('continue', True),
                "transfer_to_human": next_action.get('transfer', False),
                "confidence": confidence,
                "intent": next_action.get('intent', 'general_inquiry')
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                "text": "I understand. Let me connect you with a specialist who can help you better.",
                "continue_conversation": False,
                "transfer_to_human": True
            }
    
    async def analyze_transcription(self, transcription: str, call_id: str) -> Dict[str, Any]:
        """Analyze call transcription for insights"""
        try:
            # Sentiment analysis
            sentiment_analysis = await self._analyze_sentiment(transcription)
            
            # Extract key information
            entities = await self._extract_entities(transcription)
            
            # Determine outcome
            outcome_analysis = await self._analyze_outcome(transcription)
            
            # Generate summary
            summary = await self._generate_call_summary(transcription)
            
            return {
                "sentiment": sentiment_analysis.get('sentiment', 'neutral'),
                "sentiment_score": sentiment_analysis.get('score', 0.5),
                "confidence": sentiment_analysis.get('confidence', 0.8),
                "entities": entities,
                "outcome": outcome_analysis.get('outcome', 'unknown'),
                "conversion_probability": outcome_analysis.get('probability', 50.0),
                "next_best_action": outcome_analysis.get('next_action', 'Schedule follow-up'),
                "objections": entities.get('objections', []),
                "summary": summary,
                "intent": entities.get('intent', 'general_inquiry'),
                "topics": entities.get('topics', []),
                "action_items": entities.get('action_items', [])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing transcription: {e}")
            return {"error": str(e)}
    
    async def optimize_agent_performance(self, agent_id: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize AI agent performance based on data"""
        try:
            # Analyze performance patterns
            analysis = await self._analyze_agent_performance(agent_id, performance_data)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(analysis)
            
            return {
                "current_score": performance_data.get('performance_score', 90.0),
                "optimization_potential": recommendations.get('potential_improvement', 5.0),
                "recommendations": recommendations.get('actions', []),
                "focus_areas": recommendations.get('focus_areas', []),
                "estimated_impact": recommendations.get('impact', 'medium')
            }
            
        except Exception as e:
            logger.error(f"Error optimizing agent {agent_id}: {e}")
            return {"error": str(e)}
    
    async def detect_high_value_prospects(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect high-value prospects using AI"""
        try:
            # Score prospect based on multiple factors
            prospect_score = await self._calculate_prospect_score(call_data)
            
            # Determine if high-value
            is_high_value = prospect_score > 80
            
            return {
                "is_high_value": is_high_value,
                "score": prospect_score,
                "value_indicators": await self._get_value_indicators(call_data),
                "recommended_actions": await self._get_prospect_recommendations(prospect_score)
            }
            
        except Exception as e:
            logger.error(f"Error detecting high-value prospect: {e}")
            return {"is_high_value": False, "score": 50.0}
    
    async def _get_call_context(self, call_id: str) -> Dict[str, Any]:
        """Get call context for analysis"""
        # This would fetch from database
        return {
            "transcript": [],
            "customer_info": {},
            "campaign_info": {},
            "agent_info": {}
        }
    
    async def _analyze_conversation(self, transcript: List[Dict], customer_info: Dict, campaign_info: Dict) -> Dict[str, Any]:
        """Analyze conversation using AI"""
        try:
            # Convert transcript to text
            conversation_text = "\n".join([
                f"{msg['speaker']}: {msg['text']}" for msg in transcript
            ])
            
            # Use OpenAI for analysis
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert call analyzer. Analyze the conversation and provide:
                        1. Conversion probability (0-100)
                        2. Next best action
                        3. Detected objections
                        4. Overall sentiment (-1 to 1)
                        5. Recommendations
                        
                        Return as JSON format."""
                    },
                    {
                        "role": "user",
                        "content": f"Conversation:\n{conversation_text}\n\nCustomer: {customer_info}\nCampaign: {campaign_info}"
                    }
                ],
                max_tokens=300
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                return json.loads(analysis_text)
            except json.JSONDecodeError:
                # Fallback parsing
                return self._parse_analysis_fallback(analysis_text)
                
        except Exception as e:
            logger.error(f"Error in conversation analysis: {e}")
            return self._get_default_insights()
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze sentiment. Return JSON with sentiment (positive/negative/neutral), score (-1 to 1), and confidence (0 to 1)."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=100
            )
            
            result = response.choices[0].message.content
            try:
                return json.loads(result)
            except:
                return {"sentiment": "neutral", "score": 0.0, "confidence": 0.5}
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"sentiment": "neutral", "score": 0.0, "confidence": 0.5}
    
    async def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "Extract entities: intent, topics, objections, action_items. Return as JSON."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=200
            )
            
            result = response.choices[0].message.content
            try:
                return json.loads(result)
            except:
                return {"intent": "general", "topics": [], "objections": [], "action_items": []}
                
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {"intent": "general", "topics": [], "objections": [], "action_items": []}
    
    async def _analyze_outcome(self, text: str) -> Dict[str, Any]:
        """Analyze call outcome"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze call outcome. Return JSON with outcome, probability (0-100), next_action."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=150
            )
            
            result = response.choices[0].message.content
            try:
                return json.loads(result)
            except:
                return {"outcome": "unknown", "probability": 50.0, "next_action": "Follow up"}
                
        except Exception as e:
            logger.error(f"Error analyzing outcome: {e}")
            return {"outcome": "unknown", "probability": 50.0, "next_action": "Follow up"}
    
    async def _generate_call_summary(self, text: str) -> str:
        """Generate call summary"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a concise call summary in 2-3 sentences."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=100
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Call summary unavailable"
    
    def _get_agent_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for AI agent"""
        return """You are a professional AI sales assistant. Be helpful, empathetic, and goal-oriented.
        
        Guidelines:
        - Listen actively and ask relevant questions
        - Address objections professionally
        - Focus on customer needs and benefits
        - Be conversational but professional
        - Keep responses concise (1-2 sentences)
        
        Your goal is to help the customer and potentially schedule an appointment if they're interested."""
    
    async def _determine_next_action(self, customer_message: str, ai_response: str) -> Dict[str, Any]:
        """Determine next action in conversation"""
        # Simple rule-based logic for demo
        transfer_keywords = ["human", "person", "manager", "supervisor", "transfer"]
        end_keywords = ["goodbye", "bye", "thank you", "not interested", "call back later"]
        
        if any(keyword in customer_message.lower() for keyword in transfer_keywords):
            return {"continue": False, "transfer": True, "intent": "transfer_request"}
        elif any(keyword in customer_message.lower() for keyword in end_keywords):
            return {"continue": False, "transfer": False, "intent": "end_call"}
        else:
            return {"continue": True, "transfer": False, "intent": "continue_conversation"}
    
    async def _get_conversation_context(self, call_sid: str) -> Dict[str, Any]:
        """Get conversation context"""
        # This would fetch conversation history from database
        return {
            "call_history": [],
            "customer_profile": {},
            "campaign_info": {}
        }
    
    def _get_default_insights(self) -> Dict[str, Any]:
        """Get default AI insights when analysis fails"""
        return {
            "conversion_probability": 50.0,
            "next_best_action": "Continue building rapport and understanding customer needs",
            "objections": [],
            "sentiment": 0.5,
            "recommendations": ["Listen actively", "Ask qualifying questions"],
            "confidence": 0.6
        }
    
    def _parse_analysis_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails"""
        # Simple text parsing fallback
        return {
            "conversion_probability": 60.0,
            "next_best_action": "Continue conversation",
            "objections": [],
            "sentiment": 0.6,
            "recommendations": []
        }
    
    async def _analyze_agent_performance(self, agent_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze agent performance patterns"""
        # This would include complex performance analysis
        return {
            "strengths": ["rapport_building", "objection_handling"],
            "weaknesses": ["closing", "urgency_creation"],
            "patterns": {"peak_hours": ["14:00-16:00"], "success_rate_trend": "increasing"}
        }
    
    async def _generate_optimization_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimization recommendations"""
        return {
            "potential_improvement": 8.5,
            "actions": [
                "Improve closing techniques",
                "Add urgency in presentations",
                "Focus on benefit-driven language"
            ],
            "focus_areas": ["closing", "urgency"],
            "impact": "high"
        }
    
    async def _calculate_prospect_score(self, call_data: Dict[str, Any]) -> float:
        """Calculate prospect value score"""
        # This would use ML model or complex scoring logic
        base_score = 50.0
        
        # Add scoring based on various factors
        if call_data.get('engagement_level') == 'high':
            base_score += 20
        if call_data.get('budget_qualified'):
            base_score += 15
        if call_data.get('decision_maker'):
            base_score += 10
        
        return min(base_score, 100.0)
    
    async def _get_value_indicators(self, call_data: Dict[str, Any]) -> List[str]:
        """Get value indicators for prospect"""
        indicators = []
        
        if call_data.get('engagement_level') == 'high':
            indicators.append("High engagement")
        if call_data.get('budget_qualified'):
            indicators.append("Budget qualified")
        if call_data.get('timeline') == 'immediate':
            indicators.append("Immediate timeline")
            
        return indicators
    
    async def _get_prospect_recommendations(self, score: float) -> List[str]:
        """Get recommendations based on prospect score"""
        if score >= 80:
            return ["Priority follow-up", "Schedule immediate appointment", "Involve senior team member"]
        elif score >= 60:
            return ["Standard follow-up", "Send additional information", "Schedule callback"]
        else:
            return ["Nurture campaign", "Educational content", "Long-term follow-up"]

---

# apps/call-center/src/core/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Vocelio Call Center Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    WORKERS: int = 4
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vocelio_call_center"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # Authentication
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    FALLBACK_PHONE_NUMBER: str = "+1234567890"
    
    # Webhooks
    WEBHOOK_BASE_URL: str = "https://your-call-center-service.railway.app"
    
    # AI Services
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Recording
    RECORDING_ENABLED: bool = True
    RECORDING_TRANSCRIPTION_ENABLED: bool = True
    RECORDING_RETENTION_DAYS: int = 365
    
    # File Storage
    STORAGE_TYPE: str = "s3"  # s3, gcs, local
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "vocelio-call-recordings"
    AWS_REGION: str = "us-east-1"
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Security
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://app.vocelio.ai",
        "https://vocelio.ai"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # Performance
    MAX_CONCURRENT_CALLS: int = 10000
    WEBSOCKET_MAX_CONNECTIONS: int = 1000
    
    # Features
    AI_INSIGHTS_ENABLED: bool = True
    REAL_TIME_MONITORING: bool = True
    AUTO_OPTIMIZATION: bool = True
    COMPLIANCE_CHECKS: bool = True
    
    # External Services
    CRM_INTEGRATION_ENABLED: bool = False
    ANALYTICS_SERVICE_URL: str = "http://analytics-pro:8009"
    AI_BRAIN_SERVICE_URL: str = "http://ai-brain:8010"
    VOICE_LAB_SERVICE_URL: str = "http://voice-lab:8006"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

---

# apps/call-center/src/core/celery.py
from celery import Celery
from core.config import settings

# Create Celery app
celery_app = Celery(
    "call_center",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "core.tasks.recording_tasks",
        "core.tasks.analysis_tasks",
        "core.tasks.cleanup_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-old-recordings": {
        "task": "core.tasks.cleanup_tasks.cleanup_old_recordings",
        "schedule": 3600.0 * 24,  # Daily
    },
    "update-agent-performance": {
        "task": "core.tasks.analysis_tasks.update_agent_performance",
        "schedule": 3600.0,  # Hourly
    },
    "generate-analytics": {
        "task": "core.tasks.analysis_tasks.generate_analytics",
        "schedule": 3600.0 * 6,  # Every 6 hours
    },
}

---

# apps/call-center/.env.example
# Application
APP_NAME=Vocelio Call Center Service
VERSION=1.0.0
DEBUG=false
PORT=8003

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/vocelio_call_center

# Redis
REDIS_URL=redis://localhost:6379/0

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Twilio
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
FALLBACK_PHONE_NUMBER=+1234567890

# Webhooks
WEBHOOK_BASE_URL=https://your-call-center-service.railway.app

# AI Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# AWS (for recordings)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=vocelio-call-recordings
AWS_REGION=us-east-1

# Monitoring
SENTRY_DSN=your_sentry_dsn_optional

# External Services
ANALYTICS_SERVICE_URL=http://analytics-pro:8009
AI_BRAIN_SERVICE_URL=http://ai-brain:8010
VOICE_LAB_SERVICE_URL=http://voice-lab:8006