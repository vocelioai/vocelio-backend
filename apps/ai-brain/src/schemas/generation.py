"""
AI Brain Pydantic Schemas
Data validation and serialization schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Generation Schemas
class OptimizationLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"

class ConversationRequest(BaseModel):
    """Request for AI conversation generation"""
    message: str = Field(..., description="Input message to process")
    agent_id: str = Field(..., description="AI agent identifier")
    context: Dict[str, Any] = Field(default_factory=dict, description="Conversation context")
    optimization_level: OptimizationLevel = Field(default=OptimizationLevel.HIGH)
    industry: Optional[str] = Field(None, description="Industry context")
    target_outcome: Optional[str] = Field(None, description="Desired conversation outcome")
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v

class ConversationResponse(BaseModel):
    """AI conversation generation response"""
    generated_text: str = Field(..., description="AI generated response")
    confidence_score: float = Field(..., ge=0, le=1, description="Response confidence (0-1)")
    optimization_applied: bool = Field(default=True)
    context_analysis: Dict[str, Any] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: Optional[int] = Field(None)
    
class ConversationContext(BaseModel):
    """Conversation context information"""
    agent_id: str
    recent_conversations: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    optimization_history: List[Dict[str, Any]]
    context_score: float = Field(..., ge=0, le=100)

class OptimizationRequest(BaseModel):
    """Request for response optimization"""
    original_response: str = Field(..., description="Original AI response")
    context: Dict[str, Any] = Field(default_factory=dict)
    target_metrics: Dict[str, float] = Field(default_factory=dict)
    optimization_goals: List[str] = Field(default_factory=list)

class OptimizationResponse(BaseModel):
    """Optimization result"""
    optimized_text: str
    improvement_score: float = Field(..., ge=0, le=100)
    changes_applied: List[str]
    expected_impact: Dict[str, float]
    confidence: float = Field(..., ge=0, le=1)

class GenerationMetrics(BaseModel):
    """AI generation performance metrics"""
    total_generations: int
    average_confidence: float
    success_rate: float
    optimization_impact: float
    response_time_avg: float
    accuracy_rate: float
    revenue_impact: Optional[float] = None

# Insights Schemas
class InsightType(str, Enum):
    CRITICAL = "critical"
    OPTIMIZATION = "optimization" 
    TREND = "trend"
    PREDICTION = "prediction"
    WARNING = "warning"
    INFO = "info"

class LiveInsight(BaseModel):
    """Live AI insight matching frontend format"""
    id: str
    type: InsightType
    title: str = Field(..., description="Insight title with emoji")
    description: str = Field(..., description="Detailed insight description")
    impact: str = Field(..., description="Business impact description")
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage")
    action: str = Field(..., description="Recommended action")
    timestamp: str = Field(..., description="Human readable timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "insight_001",
                "type": "critical",
                "title": "🚨 Ultra High-Value Prospect Alert",
                "description": "AI detected 2,847 prospects with 95%+ booking probability",
                "impact": "$47M potential revenue",
                "confidence": 98.7,
                "action": "Priority dialing recommended",
                "timestamp": "2m ago"
            }
        }

class OptimizationRecommendation(BaseModel):
    """AI optimization recommendation"""
    id: str
    category: str = Field(..., description="Optimization category")
    title: str
    description: str
    impact_score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    effort_required: str = Field(..., description="Implementation effort level")
    estimated_revenue_impact: Optional[float] = None
    implementation_time: Optional[str] = None
    prerequisites: List[str] = Field(default_factory=list)

class PerformanceAlert(BaseModel):
    """AI performance alert"""
    id: str
    severity: str = Field(..., description="Alert severity level")
    category: str = Field(..., description="Alert category")
    title: str
    message: str
    affected_agents: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    created_at: datetime
    resolved: bool = Field(default=False)

class AIMetrics(BaseModel):
    """Complete AI metrics matching frontend dashboard"""
    overall_score: float = Field(..., ge=0, le=100, description="Overall AI performance score")
    optimizations_active: int = Field(..., description="Number of active optimizations")
    models_running: int = Field(..., description="Number of neural networks running")
    predictions_today: int = Field(..., description="Predictions made today")
    accuracy_rate: float = Field(..., ge=0, le=100, description="Overall accuracy rate")
    learning_rate: float = Field(..., description="Current learning rate")
    data_points: int = Field(..., description="Data points processed")
    active_connections: int = Field(..., description="Active AI connections")
    revenue_impact: Optional[float] = Field(None, description="Revenue impact from AI")
    performance_improvement: Optional[float] = Field(None, description="Performance improvement %")
    
    class Config:
        schema_extra = {
            "example": {
                "overall_score": 94.7,
                "optimizations_active": 247,
                "models_running": 15,
                "predictions_today": 89234,
                "accuracy_rate": 97.3,
                "learning_rate": 0.0023,
                "data_points": 2847392,
                "active_connections": 1847
            }
        }

# Analysis Schemas
class TextAnalysisRequest(BaseModel):
    """Request for text analysis"""
    text: str = Field(..., description="Text to analyze")
    analysis_types: List[str] = Field(default=["sentiment", "intent", "entities"])
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
class TextAnalysisResponse(BaseModel):
    """Text analysis results"""
    sentiment: Dict[str, float] = Field(..., description="Sentiment scores")
    intent: Dict[str, float] = Field(..., description="Intent classification")
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0, le=1)
    processing_time_ms: int

class SentimentAnalysisRequest(BaseModel):
    """Sentiment analysis request"""
    text: str = Field(..., min_length=1)
    context: Optional[str] = Field(None)
    include_emotions: bool = Field(default=True)
    include_confidence: bool = Field(default=True)

class SentimentAnalysisResponse(BaseModel):
    """Sentiment analysis response"""
    sentiment: str = Field(..., description="Overall sentiment: positive, negative, neutral")
    confidence: float = Field(..., ge=0, le=1)
    sentiment_scores: Dict[str, float] = Field(..., description="Detailed sentiment scores")
    emotions: Optional[Dict[str, float]] = Field(None, description="Emotion detection results")
    recommendations: List[str] = Field(default_factory=list)

# Neural Network Schemas
class NeuralNetworkStatus(BaseModel):
    """Neural network status information"""
    name: str
    type: str = Field(..., description="Network architecture type")
    accuracy: float = Field(..., ge=0, le=100)
    status: str = Field(..., description="active, training, idle")
    description: str
    neurons: int = Field(..., description="Number of neurons")
    layers: int = Field(..., description="Number of layers")
    training_data: str = Field(..., description="Training data size")
    last_updated: Optional[datetime] = None
    performance_metrics: Dict[str, float] = Field(default_factory=dict)

class NeuralNetworkRequest(BaseModel):
    """Request to create/update neural network"""
    name: str = Field(..., min_length=1)
    type: str = Field(..., description="Architecture type")
    description: str
    config: Dict[str, Any] = Field(..., description="Network configuration")
    training_data_source: Optional[str] = None

# Training Schemas  
class TrainingSessionRequest(BaseModel):
    """Model training session request"""
    model_name: str = Field(..., description="Model to train")
    training_data: Dict[str, Any] = Field(..., description="Training dataset")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    validation_split: float = Field(default=0.2, ge=0.1, le=0.5)
    epochs: int = Field(default=10, ge=1, le=1000)

class TrainingSessionResponse(BaseModel):
    """Training session results"""
    session_id: str
    status: str = Field(..., description="Training status")
    progress: float = Field(..., ge=0, le=100)
    current_epoch: int
    total_epochs: int
    metrics: Dict[str, float] = Field(default_factory=dict)
    estimated_completion: Optional[datetime] = None

class ModelPerformanceMetrics(BaseModel):
    """Model performance metrics"""
    model_name: str
    accuracy: float = Field(..., ge=0, le=100)
    precision: float = Field(..., ge=0, le=1)
    recall: float = Field(..., ge=0, le=1)
    f1_score: float = Field(..., ge=0, le=1)
    training_time: float = Field(..., description="Training time in seconds")
    inference_time_ms: float = Field(..., description="Average inference time")
    
# Prediction Schemas
class PredictionRequest(BaseModel):
    """AI prediction request"""
    prediction_type: str = Field(..., description="Type of prediction")
    input_data: Dict[str, Any] = Field(..., description="Input data for prediction")
    time_horizon: Optional[str] = Field("30d", description="Prediction time horizon")
    confidence_threshold: float = Field(default=0.8, ge=0, le=1)

class PredictionResponse(BaseModel):
    """AI prediction response"""
    prediction_id: str
    prediction_type: str
    results: Dict[str, Any] = Field(..., description="Prediction results")
    confidence: float = Field(..., ge=0, le=1)
    methodology: str = Field(..., description="Prediction methodology used")
    created_at: datetime
    expires_at: Optional[datetime] = None

# Language Processing Schemas
class LanguageDetectionRequest(BaseModel):
    """Language detection request"""
    text: str = Field(..., min_length=1)
    include_confidence: bool = Field(default=True)

class LanguageDetectionResponse(BaseModel):
    """Language detection response"""
    detected_language: str = Field(..., description="ISO language code")
    confidence: float = Field(..., ge=0, le=1)
    alternative_languages: List[Dict[str, float]] = Field(default_factory=list)

class TranslationRequest(BaseModel):
    """Text translation request"""
    text: str = Field(..., min_length=1)
    source_language: Optional[str] = Field(None, description="Source language (auto-detect if None)")
    target_language: str = Field(..., description="Target language code")
    preserve_formatting: bool = Field(default=True)

class TranslationResponse(BaseModel):
    """Translation response"""
    translated_text: str
    source_language: str
    target_language: str
    confidence: float = Field(..., ge=0, le=1)
    
# Optimization Schemas
class ResponseOptimization(BaseModel):
    """Response optimization configuration"""
    optimize_for: List[str] = Field(default=["conversion", "engagement", "clarity"])
    target_metrics: Dict[str, float] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    a_b_test: bool = Field(default=False)

class OptimizationTask(BaseModel):
    """Optimization task tracking"""
    task_id: str
    user_id: str
    agent_ids: List[str]
    optimization_type: str
    status: str = Field(..., description="pending, running, completed, failed")
    progress: float = Field(default=0, ge=0, le=100)
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

# WebSocket Schemas
class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str = Field(..., description="Message type")
    data: Any = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class InsightUpdate(BaseModel):
    """Real-time insight update"""
    insight: LiveInsight
    update_type: str = Field(..., description="new, updated, resolved")
    affected_agents: List[str] = Field(default_factory=list)

# Error Response Schemas
class AIErrorResponse(BaseModel):
    """AI service error response"""
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
    suggested_actions: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Batch Operation Schemas
class BatchOptimizationRequest(BaseModel):
    """Batch optimization request"""
    agent_ids: List[str] = Field(..., min_items=1, max_items=100)
    optimization_goals: Dict[str, Any] = Field(..., description="Optimization objectives")
    priority: str = Field(default="normal", description="Processing priority")
    notify_completion: bool = Field(default=True)

class BatchOptimizationResponse(BaseModel):
    """Batch optimization response"""
    task_id: str
    status: str
    agents_count: int
    estimated_completion_minutes: int
    priority: str
    created_at: datetime

# Feedback Schemas
class ConversationFeedback(BaseModel):
    """Conversation feedback for learning"""
    conversation_id: str
    agent_id: str
    feedback_score: float = Field(..., ge=0, le=10, description="Feedback score 0-10")
    feedback_text: Optional[str] = Field(None, max_length=1000)
    feedback_categories: List[str] = Field(default_factory=list)
    improvement_suggestions: Optional[str] = None

class FeedbackAnalysis(BaseModel):
    """Feedback analysis results"""
    feedback_id: str
    sentiment_analysis: Dict[str, float]
    key_insights: List[str]
    improvement_areas: List[str]
    confidence: float = Field(..., ge=0, le=1)
    learning_impact: str = Field(..., description="Impact on model learning")

# Configuration Schemas
class AIConfiguration(BaseModel):
    """AI service configuration"""
    model_settings: Dict[str, Any] = Field(default_factory=dict)
    optimization_settings: Dict[str, Any] = Field(default_factory=dict)
    performance_thresholds: Dict[str, float] = Field(default_factory=dict)
    auto_optimization_enabled: bool = Field(default=True)
    real_time_learning: bool = Field(default=True)
    
class ModelConfiguration(BaseModel):
    """Individual model configuration"""
    model_name: str
    model_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    training_config: Dict[str, Any] = Field(default_factory=dict)
    deployment_config: Dict[str, Any] = Field(default_factory=dict)
    
# Health Check Schemas
class AIHealthStatus(BaseModel):
    """AI service health status"""
    service_status: str = Field(..., description="Service health status")
    models_status: Dict[str, str] = Field(default_factory=dict)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    last_health_check: datetime
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

# Analytics Integration Schemas
class AnalyticsEvent(BaseModel):
    """Analytics event for tracking"""
    event_type: str = Field(..., description="Type of analytics event")
    agent_id: Optional[str] = None
    user_id: str
    event_data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None

class PerformanceReport(BaseModel):
    """AI performance report"""
    report_id: str
    user_id: str
    time_period: str
    summary_metrics: Dict[str, float]
    detailed_analysis: Dict[str, Any]
    recommendations: List[OptimizationRecommendation]
    generated_at: datetime
    report_format: str = Field(default="json", description="Report format")

# Real-time Monitoring Schemas
class RealTimeMetrics(BaseModel):
    """Real-time AI monitoring metrics"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    active_models: int
    processing_queue_size: int
    average_response_time: float
    error_rate: float = Field(..., ge=0, le=1)
    throughput_per_second: float
    resource_utilization: Dict[str, float] = Field(default_factory=dict)

class SystemAlert(BaseModel):
    """System-level alert"""
    alert_id: str
    alert_type: str = Field(..., description="Type of system alert")
    severity: str = Field(..., description="Alert severity")
    component: str = Field(..., description="Affected system component")
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    auto_resolved: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None