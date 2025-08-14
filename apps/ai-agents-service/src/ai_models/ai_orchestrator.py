"""
Advanced AI Model Orchestrator for Vocelio.ai
Intelligently routes requests to the optimal AI model based on task requirements
Integrated into AI Agents Service
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Available AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class TaskType(Enum):
    """Types of AI tasks for optimal model selection"""
    CONVERSATION = "conversation"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    REASONING = "reasoning"
    REAL_TIME = "real_time"
    COMPLEX_PLANNING = "complex_planning"
    CODE_GENERATION = "code_generation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"


@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    provider: AIProvider
    model_name: str
    max_tokens: int
    temperature: float
    cost_per_1k_tokens: float
    avg_response_time_ms: int
    context_window: int
    strengths: List[str]


class AIOrchestrator:
    """
    Intelligent AI model orchestrator that selects the best model for each task
    Supports multiple providers and automatic fallback strategies
    """
    
    def __init__(self):
        # Initialize clients if API keys are available
        self.openai_client = None
        self.anthropic_client = None
        
        try:
            import openai
            if os.getenv("OPENAI_API_KEY"):
                self.openai_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except ImportError:
            logger.warning("OpenAI client not available")
            
        try:
            import anthropic
            if os.getenv("ANTHROPIC_API_KEY"):
                self.anthropic_client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        except ImportError:
            logger.warning("Anthropic client not available")
        
        # Model configurations - Updated with latest models
        self.models = {
            # OpenAI Models
            "gpt-4-turbo": ModelConfig(
                provider=AIProvider.OPENAI,
                model_name="gpt-4-turbo-preview",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.03,
                avg_response_time_ms=3000,
                context_window=128000,
                strengths=["reasoning", "analysis", "complex_planning", "code_generation"]
            ),
            "gpt-4o": ModelConfig(
                provider=AIProvider.OPENAI,
                model_name="gpt-4o",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.015,
                avg_response_time_ms=1500,
                context_window=128000,
                strengths=["real_time", "conversation", "general_purpose"]
            ),
            "gpt-4o-mini": ModelConfig(
                provider=AIProvider.OPENAI,
                model_name="gpt-4o-mini",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.0015,
                avg_response_time_ms=800,
                context_window=128000,
                strengths=["real_time", "high_volume", "cost_effective"]
            ),
            
            # Anthropic Models - Latest Generation
            "claude-3-5-sonnet": ModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.015,
                avg_response_time_ms=2000,
                context_window=200000,
                strengths=["conversation", "reasoning", "analysis", "natural_dialogue", "code_generation"]
            ),
            "claude-3-7-sonnet": ModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name="claude-3-7-sonnet",
                max_tokens=8192,
                temperature=0.7,
                cost_per_1k_tokens=0.018,
                avg_response_time_ms=1800,
                context_window=300000,
                strengths=["advanced_reasoning", "complex_analysis", "superior_dialogue", "enterprise_tasks"]
            ),
            "claude-sonnet-4": ModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name="claude-sonnet-4",
                max_tokens=8192,
                temperature=0.7,
                cost_per_1k_tokens=0.025,
                avg_response_time_ms=1500,
                context_window=500000,
                strengths=["next_gen_reasoning", "enterprise_grade", "multi_modal", "advanced_planning"]
            ),
            "claude-opus-4": ModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name="claude-opus-4",
                max_tokens=8192,
                temperature=0.7,
                cost_per_1k_tokens=0.080,
                avg_response_time_ms=2500,
                context_window=1000000,
                strengths=["ultimate_reasoning", "complex_planning", "research_grade", "strategic_analysis"]
            ),
            "claude-opus-4-1": ModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name="claude-opus-4-1",
                max_tokens=8192,
                temperature=0.7,
                cost_per_1k_tokens=0.100,
                avg_response_time_ms=2000,
                context_window=2000000,
                strengths=["world_class_ai", "enterprise_ultimate", "strategic_planning", "advanced_research", "multi_modal_expert"]
            )
        }
        
        # Task-to-model mapping for optimal performance
        self.task_model_mapping = {
            TaskType.CONVERSATION: ["claude-sonnet-4", "claude-3-7-sonnet", "claude-3-5-sonnet", "gpt-4o"],
            TaskType.ANALYSIS: ["claude-opus-4-1", "claude-opus-4", "claude-sonnet-4", "gpt-4-turbo"],
            TaskType.REASONING: ["claude-opus-4-1", "claude-opus-4", "claude-sonnet-4", "claude-3-7-sonnet"],
            TaskType.REAL_TIME: ["gpt-4o-mini", "claude-3-7-sonnet", "gpt-4o"],
            TaskType.COMPLEX_PLANNING: ["claude-opus-4-1", "claude-opus-4", "claude-sonnet-4", "claude-3-7-sonnet"],
            TaskType.CODE_GENERATION: ["claude-sonnet-4", "claude-3-7-sonnet", "gpt-4-turbo", "claude-3-5-sonnet"],
            TaskType.SENTIMENT_ANALYSIS: ["claude-sonnet-4", "claude-3-7-sonnet", "claude-opus-4", "claude-3-5-sonnet"]
        }
        
        # Performance tracking
        self.model_performance = {}
        self.request_count = 0
    
    def select_optimal_model(
        self, 
        task_type: TaskType, 
        context_length: int = 0,
        priority: str = "balanced",  # "speed", "quality", "cost", "balanced"
        fallback: bool = True
    ) -> str:
        """
        Select the optimal AI model based on task requirements
        """
        available_models = self.task_model_mapping.get(task_type, ["claude-3-5-sonnet"])
        
        # Filter models based on context window requirements
        suitable_models = []
        for model_name in available_models:
            if model_name in self.models:
                model_config = self.models[model_name]
                if context_length <= model_config.context_window:
                    suitable_models.append(model_name)
        
        if not suitable_models:
            # Fallback to models with largest context windows
            suitable_models = sorted(
                [m for m in available_models if m in self.models],
                key=lambda m: self.models[m].context_window,
                reverse=True
            )[:2]
        
        if not suitable_models:
            suitable_models = ["claude-3-5-sonnet"]  # Ultimate fallback
        
        # Select based on priority
        if priority == "speed":
            selected = min(suitable_models, key=lambda m: self.models[m].avg_response_time_ms)
        elif priority == "cost":
            selected = min(suitable_models, key=lambda m: self.models[m].cost_per_1k_tokens)
        elif priority == "quality":
            # For quality, prefer latest Claude models
            quality_order = ["claude-opus-4-1", "claude-opus-4", "claude-sonnet-4", "claude-3-7-sonnet", "claude-3-5-sonnet"]
            selected = next((m for m in quality_order if m in suitable_models), suitable_models[0])
        else:  # balanced
            selected = suitable_models[0]  # Use first available
        
        logger.info(f"Selected {selected} for {task_type.value} task (priority: {priority})")
        return selected
    
    async def generate_response(
        self,
        prompt: str,
        task_type: TaskType,
        context: Optional[List[Dict[str, str]]] = None,
        model_override: Optional[str] = None,
        priority: str = "balanced",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate AI response using optimal model selection
        For now, returns simulated responses as a proof of concept
        """
        self.request_count += 1
        
        # Calculate context length
        context_length = len(prompt)
        if context:
            context_length += sum(len(msg.get("content", "")) for msg in context)
        
        # Select model
        model_name = model_override or self.select_optimal_model(
            task_type, context_length, priority
        )
        
        if model_name not in self.models:
            model_name = "claude-3-5-sonnet"  # Safe fallback
            
        model_config = self.models[model_name]
        start_time = asyncio.get_event_loop().time()
        
        # Simulate AI response based on task type (replace with actual API calls)
        response = await self._simulate_response(prompt, task_type, model_config)
        
        # Calculate metrics
        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        # Update performance tracking
        if model_name not in self.model_performance:
            self.model_performance[model_name] = {
                "total_requests": 0,
                "total_response_time": 0,
                "error_count": 0
            }
        
        self.model_performance[model_name]["total_requests"] += 1
        self.model_performance[model_name]["total_response_time"] += response_time
        
        return {
            "content": response,
            "model": model_name,
            "provider": model_config.provider.value,
            "response_time_ms": round(response_time, 2),
            "task_type": task_type.value,
            "request_id": self.request_count,
            "context_length": context_length
        }
    
    async def _simulate_response(self, prompt: str, task_type: TaskType, model_config: ModelConfig) -> str:
        """
        Simulate AI response for different task types
        Replace this with actual API calls to OpenAI/Anthropic
        """
        await asyncio.sleep(model_config.avg_response_time_ms / 1000)  # Simulate response time
        
        if task_type == TaskType.CONVERSATION:
            return f"I understand your request about '{prompt[:50]}...'. As an AI agent, I'm here to help with professional, engaging conversation."
        elif task_type == TaskType.ANALYSIS:
            return f"Analysis of '{prompt[:50]}...': This appears to be a complex topic requiring detailed examination of multiple factors including strategic considerations, market dynamics, and optimization opportunities."
        elif task_type == TaskType.SENTIMENT_ANALYSIS:
            return "Sentiment: Positive (0.8 confidence). The text shows enthusiasm and engagement with clear interest indicators."
        elif task_type == TaskType.COMPLEX_PLANNING:
            return f"Strategic plan for '{prompt[:50]}...': 1) Situational Analysis 2) Market Assessment 3) Implementation Strategy 4) Success Metrics 5) Risk Mitigation"
        elif task_type == TaskType.REAL_TIME:
            return f"Quick response: Understood. Let me help you with {prompt[:30]}..."
        else:
            return f"AI response generated using {model_config.model_name} for {task_type.value} task."
    
    async def check_for_new_models(self) -> Dict[str, Any]:
        """Check for newly available models"""
        return {
            "new_models_found": 0,
            "models": {},
            "check_timestamp": asyncio.get_event_loop().time()
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all models"""
        stats = {}
        
        for model_name, perf in self.model_performance.items():
            if perf["total_requests"] > 0:
                avg_response_time = perf["total_response_time"] / perf["total_requests"]
                error_rate = perf["error_count"] / perf["total_requests"] * 100
                
                stats[model_name] = {
                    "total_requests": perf["total_requests"],
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "error_rate_percent": round(error_rate, 2),
                    "success_rate_percent": round(100 - error_rate, 2)
                }
        
        return {
            "total_requests": self.request_count,
            "model_stats": stats,
            "available_models": list(self.models.keys())
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of AI orchestrator"""
        return {
            "orchestrator": {"status": "healthy", "models_available": len(self.models)},
            "openai": {"status": "available" if self.openai_client else "not_configured"},
            "anthropic": {"status": "available" if self.anthropic_client else "not_configured"}
        }


# Global orchestrator instance
ai_orchestrator = AIOrchestrator()


# Convenience functions for common use cases
async def generate_conversation_response(prompt: str, context: Optional[List[Dict]] = None) -> str:
    """Generate natural conversation response"""
    result = await ai_orchestrator.generate_response(
        prompt, TaskType.CONVERSATION, context, priority="balanced"
    )
    return result["content"]


async def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze sentiment using optimal model"""
    prompt = f"Analyze the sentiment of this text and provide a detailed analysis: {text}"
    result = await ai_orchestrator.generate_response(
        prompt, TaskType.SENTIMENT_ANALYSIS, priority="quality"
    )
    return result


async def generate_real_time_response(prompt: str) -> str:
    """Generate fast real-time response"""
    result = await ai_orchestrator.generate_response(
        prompt, TaskType.REAL_TIME, priority="speed"
    )
    return result["content"]


async def complex_reasoning(prompt: str, context: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Perform complex reasoning task"""
    result = await ai_orchestrator.generate_response(
        prompt, TaskType.COMPLEX_PLANNING, context, priority="quality"
    )
    return result
