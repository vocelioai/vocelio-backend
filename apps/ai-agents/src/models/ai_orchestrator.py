"""
Advanced AI Model Orchestrator for Vocelio.ai
Intelligently routes requests to the optimal AI model based on task requirements
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass
import openai
import anthropic
from ..config import settings

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
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        
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
            
            # Anthropic Models - Latest Generation (Available via Copilot Pro+)
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
            ),
            "claude-3-opus": ModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name="claude-3-opus-20240229",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.075,
                avg_response_time_ms=4000,
                context_window=200000,
                strengths=["complex_planning", "advanced_reasoning", "creative_tasks", "research"]
            ),
            "claude-3-haiku": ModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name="claude-3-haiku-20240307",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.0025,
                avg_response_time_ms=500,
                context_window=200000,
                strengths=["real_time", "fast_responses", "cost_effective"]
            )
        }
        
        # Task-to-model mapping for optimal performance
        # Prioritizing newest Claude models (Opus 4.1, Sonnet 4, Claude 3.7)
        self.task_model_mapping = {
            TaskType.CONVERSATION: ["claude-sonnet-4", "claude-3-7-sonnet", "claude-3-5-sonnet", "gpt-4o"],
            TaskType.ANALYSIS: ["claude-opus-4-1", "claude-opus-4", "claude-sonnet-4", "gpt-4-turbo"],
            TaskType.REASONING: ["claude-opus-4-1", "claude-opus-4", "claude-sonnet-4", "claude-3-7-sonnet"],
            TaskType.REAL_TIME: ["gpt-4o-mini", "claude-3-haiku", "claude-3-7-sonnet", "gpt-4o"],
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
        
        Args:
            task_type: Type of task to perform
            context_length: Length of context/conversation
            priority: Optimization priority
            fallback: Whether to use fallback models
            
        Returns:
            Selected model name
        """
        available_models = self.task_model_mapping.get(task_type, ["claude-3-5-sonnet"])
        
        # Filter models based on context window requirements
        suitable_models = []
        for model_name in available_models:
            model_config = self.models[model_name]
            if context_length <= model_config.context_window:
                suitable_models.append(model_name)
        
        if not suitable_models:
            # Fallback to models with largest context windows
            suitable_models = sorted(
                available_models,
                key=lambda m: self.models[m].context_window,
                reverse=True
            )[:2]
        
        # Select based on priority
        if priority == "speed":
            selected = min(suitable_models, key=lambda m: self.models[m].avg_response_time_ms)
        elif priority == "cost":
            selected = min(suitable_models, key=lambda m: self.models[m].cost_per_1k_tokens)
        elif priority == "quality":
            # For quality, prefer Claude 3.5 Sonnet or GPT-4 Turbo
            quality_order = ["claude-3-opus", "gpt-4-turbo", "claude-3-5-sonnet"]
            selected = next((m for m in quality_order if m in suitable_models), suitable_models[0])
        else:  # balanced
            # Score models based on balanced criteria
            scores = {}
            for model_name in suitable_models:
                config = self.models[model_name]
                # Lower is better for cost and response time, normalize scores
                cost_score = 1 / (config.cost_per_1k_tokens * 100 + 1)
                speed_score = 1 / (config.avg_response_time_ms / 1000 + 1)
                
                # Quality score based on model strengths
                quality_score = len([s for s in config.strengths if s in [task_type.value, "general_purpose"]])
                
                scores[model_name] = cost_score + speed_score + quality_score
            
            selected = max(scores.keys(), key=lambda m: scores[m])
        
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
        
        Args:
            prompt: User prompt
            task_type: Type of task
            context: Conversation context
            model_override: Specific model to use
            priority: Selection priority
            **kwargs: Additional parameters
            
        Returns:
            Response with metadata
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
        
        model_config = self.models[model_name]
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Generate response based on provider
            if model_config.provider == AIProvider.OPENAI:
                response = await self._generate_openai_response(
                    model_config, prompt, context, **kwargs
                )
            elif model_config.provider == AIProvider.ANTHROPIC:
                response = await self._generate_anthropic_response(
                    model_config, prompt, context, **kwargs
                )
            else:
                raise ValueError(f"Unsupported provider: {model_config.provider}")
            
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
            
        except Exception as e:
            logger.error(f"Error with {model_name}: {e}")
            
            # Update error count
            if model_name in self.model_performance:
                self.model_performance[model_name]["error_count"] += 1
            
            # Try fallback model if available
            fallback_models = [m for m in self.task_model_mapping[task_type] if m != model_name]
            if fallback_models:
                logger.info(f"Attempting fallback to {fallback_models[0]}")
                return await self.generate_response(
                    prompt, task_type, context, fallback_models[0], priority, **kwargs
                )
            
            raise
    
    async def _generate_openai_response(
        self,
        model_config: ModelConfig,
        prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """Generate response using OpenAI API"""
        messages = []
        
        # Add context messages
        if context:
            messages.extend(context)
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        response = await self.openai_client.chat.completions.create(
            model=model_config.model_name,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", model_config.max_tokens),
            temperature=kwargs.get("temperature", model_config.temperature),
            stream=False
        )
        
        return response.choices[0].message.content
    
    async def _generate_anthropic_response(
        self,
        model_config: ModelConfig,
        prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """Generate response using Anthropic API"""
        # Convert context to Anthropic format
        messages = []
        if context:
            for msg in context:
                role = "user" if msg["role"] == "user" else "assistant"
                messages.append({"role": role, "content": msg["content"]})
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        response = await self.anthropic_client.messages.create(
            model=model_config.model_name,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", model_config.max_tokens),
            temperature=kwargs.get("temperature", model_config.temperature)
        )
        
        return response.content[0].text
    
    async def check_for_new_models(self) -> Dict[str, Any]:
        """
        Check for newly available models from all providers
        Automatically detects Claude 4, GPT-5, and other new releases
        """
        new_models = {}
        
        # Check Anthropic for new models
        try:
            # This would check Anthropic's model list API when available
            # For now, we manually check known upcoming models
            upcoming_anthropic = [
                "claude-4",
                "claude-opus-4", 
                "claude-opus-4.1",
                "claude-4-sonnet",
                "claude-4-haiku"
            ]
            
            for model_name in upcoming_anthropic:
                try:
                    # Test if model is available
                    test_response = await self.anthropic_client.messages.create(
                        model=model_name,
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=1
                    )
                    new_models[model_name] = "Available"
                    logger.info(f"🎉 New model detected: {model_name}")
                except Exception:
                    pass  # Model not available yet
                    
        except Exception as e:
            logger.debug(f"Could not check Anthropic models: {e}")
        
        # Check OpenAI for new models
        try:
            # Check for GPT-5 and other upcoming models
            upcoming_openai = [
                "gpt-5",
                "gpt-4.5-turbo",
                "gpt-4o-ultra"
            ]
            
            for model_name in upcoming_openai:
                try:
                    test_response = await self.openai_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=1
                    )
                    new_models[model_name] = "Available"
                    logger.info(f"🎉 New model detected: {model_name}")
                except Exception:
                    pass  # Model not available yet
                    
        except Exception as e:
            logger.debug(f"Could not check OpenAI models: {e}")
        
        return {
            "new_models_found": len(new_models),
            "models": new_models,
            "check_timestamp": asyncio.get_event_loop().time()
        }
    
    async def add_future_model(self, model_name: str, config: ModelConfig):
        """Add a new model configuration when it becomes available"""
        self.models[model_name] = config
        logger.info(f"✅ Added new model: {model_name}")
        
        # Update task mappings to include the new model
        if "claude-4" in model_name or "opus-4" in model_name:
            # Claude 4 series - add to all task types as primary
            for task_type in self.task_model_mapping:
                if model_name not in self.task_model_mapping[task_type]:
                    self.task_model_mapping[task_type].insert(0, model_name)
        elif "gpt-5" in model_name:
            # GPT-5 - add to reasoning and analysis tasks
            priority_tasks = [TaskType.REASONING, TaskType.ANALYSIS, TaskType.CODE_GENERATION]
            for task_type in priority_tasks:
                if model_name not in self.task_model_mapping[task_type]:
                    self.task_model_mapping[task_type].insert(0, model_name)
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
        """Check health of all AI providers"""
        health_status = {}
        
        # Test OpenAI
        try:
            test_response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            health_status["openai"] = {"status": "healthy", "response_time": "fast"}
        except Exception as e:
            health_status["openai"] = {"status": "unhealthy", "error": str(e)}
        
        # Test Anthropic
        try:
            test_response = await self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            health_status["anthropic"] = {"status": "healthy", "response_time": "fast"}
        except Exception as e:
            health_status["anthropic"] = {"status": "unhealthy", "error": str(e)}
        
        return health_status


# Global orchestrator instance
ai_orchestrator = AIOrchestrator()


# Convenience functions for common use cases
async def generate_conversation_response(prompt: str, context: List[Dict] = None) -> str:
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


async def complex_reasoning(prompt: str, context: List[Dict] = None) -> Dict[str, Any]:
    """Perform complex reasoning task"""
    result = await ai_orchestrator.generate_response(
        prompt, TaskType.COMPLEX_PLANNING, context, priority="quality"
    )
    return result
