"""
AI Brain Database Models
SQLAlchemy/Supabase models for AI Brain service
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from shared.models.base import BaseModel, TimestampMixin

Base = declarative_base()

class Conversation(BaseModel, TimestampMixin):
    """Conversation records for AI learning"""
    __tablename__ = "ai_conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Conversation data
    input_message = Column(Text, nullable=False)
    generated_response = Column(Text, nullable=False)
    context = Column(JSON, default={})
    
    # Performance metrics
    confidence_score = Column(Float, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    optimization_applied = Column(Boolean, default=True)
    
    # Analysis results
    sentiment_analysis = Column(JSON, default={})
    intent_analysis = Column(JSON, default={})
    context_analysis = Column(JSON, default={})
    
    # Feedback and learning
    feedback_score = Column(Float, nullable=True)
    feedback_text = Column(Text, nullable=True)
    human_feedback = Column(JSON, default={})
    
    # Metadata
    model_version = Column(String, default="gpt-4-turbo")
    optimization_level = Column(String, default="high")
    session_id = Column(String, nullable=True, index=True)

class ConversationAnalysis(BaseModel, TimestampMixin):
    """Detailed conversation analysis"""
    __tablename__ = "ai_conversation_analysis"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("ai_conversations.id"), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    
    # Analysis results
    sentiment_scores = Column(JSON, nullable=False)
    emotion_scores = Column(JSON, default={})
    intent_classification = Column(JSON, nullable=False)
    entity_extraction = Column(JSON, default={})
    
    # Quality metrics
    clarity_score = Column(Float, nullable=False)
    engagement_score = Column(Float, nullable=False)
    persuasiveness_score = Column(Float, nullable=False)
    
    # Optimization insights
    optimization_opportunities = Column(JSON, default={})
    improvement_suggestions = Column(JSON, default={})
    predicted_outcome = Column(JSON, default={})
    
    # Performance tracking
    actual_outcome = Column(String, nullable=True)
    outcome_confidence = Column(Float, nullable=True)
    success_probability = Column(Float, nullable=True)

class AIOptimization(BaseModel, TimestampMixin):
    """AI optimization tasks and results"""
    __tablename__ = "ai_optimizations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=True, index=True)
    
    # Optimization details
    optimization_type = Column(String, nullable=False)  # voice, timing, script, targeting
    optimization_category = Column(String, nullable=False)  # performance, revenue, engagement
    
    # Configuration
    original_config = Column(JSON, nullable=False)
    optimized_config = Column(JSON, nullable=False)
    optimization_goals = Column(JSON, default={})
    
    # Results
    status = Column(String, default="pending")  # pending, active, completed, failed
    confidence_score = Column(Float, nullable=False)
    expected_impact = Column(JSON, default={})
    actual_impact = Column(JSON, default={})
    
    # Performance tracking
    baseline_metrics = Column(JSON, default={})
    current_metrics = Column(JSON, default={})
    improvement_percentage = Column(Float, nullable=True)
    
    # Metadata
    applied_at = Column(DateTime, nullable=True)
    reverted_at = Column(DateTime, nullable=True)
    auto_applied = Column(Boolean, default=False)

class NeuralNetwork(BaseModel, TimestampMixin):
    """Neural network model management"""
    __tablename__ = "ai_neural_networks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Network details
    name = Column(String, nullable=False)
    network_type = Column(String, nullable=False)  # transformer, cnn, rnn, etc.
    description = Column(Text, nullable=True)
    
    # Architecture
    layers = Column(Integer, nullable=False)
    neurons = Column(Integer, nullable=False)
    parameters = Column(JSON, default={})
    architecture_config = Column(JSON, nullable=False)
    
    # Performance
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Status and deployment
    status = Column(String, default="training")  # training, active, idle, failed
    deployment_status = Column(String, default="development")  # development, staging, production
    version = Column(String, default="1.0.0")
    
    # Training information
    training_data_size = Column(String, nullable=True)  # "847TB"
    training_duration = Column(Integer, nullable=True)  # seconds
    last_trained = Column(DateTime, nullable=True)
    
    # Resource usage
    memory_usage_mb = Column(Integer, nullable=True)
    cpu_usage_percent = Column(Float, nullable=True)
    gpu_usage_percent = Column(Float, nullable=True)

class TrainingSession(BaseModel, TimestampMixin):
    """Model training session tracking"""
    __tablename__ = "ai_training_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    network_id = Column(String, ForeignKey("ai_neural_networks.id"), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    
    # Training configuration
    training_config = Column(JSON, nullable=False)
    hyperparameters = Column(JSON, nullable=False)
    dataset_info = Column(JSON, nullable=False)
    
    # Progress tracking
    status = Column(String, default="pending")  # pending, running, completed, failed, cancelled
    current_epoch = Column(Integer, default=0)
    total_epochs = Column(Integer, nullable=False)
    progress_percentage = Column(Float, default=0.0)
    
    # Performance metrics
    training_loss = Column(Float, nullable=True)
    validation_loss = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    learning_rate = Column(Float, nullable=True)
    
    # Results
    final_metrics = Column(JSON, default={})
    model_artifacts = Column(JSON, default={})  # Paths to saved models
    training_logs = Column(JSON, default={})
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_completion = Column(DateTime, nullable=True)
    
    # Resources
    compute_resources = Column(JSON, default={})
    total_compute_cost = Column(Float, nullable=True)

class AIInsight(BaseModel, TimestampMixin):
    """AI-generated insights and recommendations"""
    __tablename__ = "ai_insights"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=True, index=True)
    
    # Insight details
    insight_type = Column(String, nullable=False)  # critical, optimization, trend, prediction
    category = Column(String, nullable=False)  # performance, revenue, optimization, alert
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Impact and confidence
    impact_description = Column(String, nullable=False)
    impact_score = Column(Float, nullable=False)  # 0-100
    confidence = Column(Float, nullable=False)  # 0-100
    
    # Actions
    recommended_action = Column(String, nullable=False)
    action_priority = Column(String, default="medium")  # low, medium, high, critical
    action_complexity = Column(String, default="simple")  # simple, moderate, complex
    
    # Status tracking
    status = Column(String, default="new")  # new, viewed, applied, dismissed, expired
    applied_at = Column(DateTime, nullable=True)
    applied_by = Column(String, nullable=True)
    
    # Results tracking
    expected_results = Column(JSON, default={})
    actual_results = Column(JSON, default={})
    success_metrics = Column(JSON, default={})
    
    # Metadata
    data_sources = Column(JSON, default={})
    methodology = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)

class AIPerformanceMetric(BaseModel, TimestampMixin):
    """AI performance metrics tracking"""
    __tablename__ = "ai_performance_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=True, index=True)
    
    # Metric details
    metric_type = Column(String, nullable=False)  # accuracy, performance, optimization
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String, nullable=True)
    
    # Context
    measurement_context = Column(JSON, default={})
    time_period = Column(String, nullable=True)  # 1h, 24h, 7d, 30d
    
    # Comparison data
    baseline_value = Column(Float, nullable=True)
    target_value = Column(Float, nullable=True)
    improvement_percentage = Column(Float, nullable=True)
    
    # Quality indicators
    data_quality_score = Column(Float, nullable=True)
    confidence_interval = Column(JSON, default={})
    statistical_significance = Column(Float, nullable=True)

class OptimizationTask(BaseModel, TimestampMixin):
    """Optimization task management"""
    __tablename__ = "ai_optimization_tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Task details
    task_type = Column(String, nullable=False)  # single_agent, batch, global
    task_name = Column(String, nullable=False)
    task_description = Column(Text, nullable=True)
    
    # Configuration
    target_agents = Column(JSON, default={})  # List of agent IDs
    optimization_config = Column(JSON, nullable=False)
    constraints = Column(JSON, default={})
    
    # Execution
    status = Column(String, default="pending")  # pending, running, completed, failed, cancelled
    progress_percentage = Column(Float, default=0.0)
    
    # Results
    execution_log = Column(JSON, default={})
    results_summary = Column(JSON, default={})
    performance_impact = Column(JSON, default={})
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # seconds
    
    # Error handling
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

class AIModelDeployment(BaseModel, TimestampMixin):
    """AI model deployment tracking"""
    __tablename__ = "ai_model_deployments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    network_id = Column(String, ForeignKey("ai_neural_networks.id"), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    
    # Deployment details
    deployment_name = Column(String, nullable=False)
    environment = Column(String, nullable=False)  # development, staging, production
    version = Column(String, nullable=False)
    
    # Configuration
    deployment_config = Column(JSON, nullable=False)
    resource_allocation = Column(JSON, default={})
    scaling_config = Column(JSON, default={})
    
    # Status
    status = Column(String, default="pending")  # pending, deploying, active, failed, retired
    health_status = Column(String, default="unknown")  # healthy, degraded, unhealthy
    
    # Performance
    requests_per_second = Column(Float, nullable=True)
    average_latency_ms = Column(Float, nullable=True)
    error_rate = Column(Float, nullable=True)
    uptime_percentage = Column(Float, nullable=True)
    
    # Resource usage
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    storage_usage = Column(Float, nullable=True)
    
    # Deployment lifecycle
    deployed_at = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, nullable=True)
    retired_at = Column(DateTime, nullable=True)

class AILearningEvent(BaseModel, TimestampMixin):
    """Learning events for continuous improvement"""
    __tablename__ = "ai_learning_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=True, index=True)
    conversation_id = Column(String, ForeignKey("ai_conversations.id"), nullable=True)
    
    # Event details
    event_type = Column(String, nullable=False)  # feedback, outcome, optimization
    event_source = Column(String, nullable=False)  # human, system, automated
    
    # Learning data
    input_data = Column(JSON, nullable=False)
    expected_output = Column(JSON, nullable=True)
    actual_output = Column(JSON, nullable=True)
    
    # Quality assessment
    quality_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    novelty_score = Column(Float, nullable=True)
    
    # Learning impact
    model_update_applied = Column(Boolean, default=False)
    improvement_measured = Column(JSON, default={})
    learning_weight = Column(Float, default=1.0)
    
    # Processing status
    processed = Column(Boolean, default=False)
    processing_results = Column(JSON, default={})
    processing_errors = Column(JSON, default={})

class PredictionModel(BaseModel, TimestampMixin):
    """Prediction model management"""
    __tablename__ = "ai_prediction_models"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Model details
    model_name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # revenue, outcome, performance, timing
    description = Column(Text, nullable=True)
    
    # Model configuration
    algorithm = Column(String, nullable=False)  # random_forest, linear_regression, neural_network
    hyperparameters = Column(JSON, nullable=False)
    feature_config = Column(JSON, nullable=False)
    
    # Training data
    training_dataset_id = Column(String, nullable=True)
    training_records_count = Column(Integer, nullable=True)
    validation_split = Column(Float, default=0.2)
    
    # Performance metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    mse = Column(Float, nullable=True)  # Mean Squared Error
    mae = Column(Float, nullable=True)  # Mean Absolute Error
    r2_score = Column(Float, nullable=True)
    
    # Deployment info
    status = Column(String, default="training")  # training, ready, deployed, deprecated
    deployment_endpoint = Column(String, nullable=True)
    model_file_path = Column(String, nullable=True)
    
    # Usage tracking
    prediction_count = Column(Integer, default=0)
    last_prediction = Column(DateTime, nullable=True)
    average_prediction_time_ms = Column(Float, nullable=True)

class AIPrediction(BaseModel, TimestampMixin):
    """AI predictions and forecasts"""
    __tablename__ = "ai_predictions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String, ForeignKey("ai_prediction_models.id"), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=True, index=True)
    
    # Prediction details
    prediction_type = Column(String, nullable=False)
    input_features = Column(JSON, nullable=False)
    prediction_result = Column(JSON, nullable=False)
    
    # Confidence and quality
    confidence_score = Column(Float, nullable=False)
    uncertainty_range = Column(JSON, nullable=True)
    prediction_horizon = Column(String, nullable=True)  # 1d, 7d, 30d, 90d
    
    # Validation
    actual_outcome = Column(JSON, nullable=True)
    accuracy_score = Column(Float, nullable=True)
    prediction_error = Column(Float, nullable=True)
    
    # Context
    market_conditions = Column(JSON, default={})
    external_factors = Column(JSON, default={})
    prediction_context = Column(JSON, default={})
    
    # Lifecycle
    expires_at = Column(DateTime, nullable=True)
    validated_at = Column(DateTime, nullable=True)
    invalidated_at = Column(DateTime, nullable=True)

class AIAlert(BaseModel, TimestampMixin):
    """AI-generated alerts and notifications"""
    __tablename__ = "ai_alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=True, index=True)
    
    # Alert details
    alert_type = Column(String, nullable=False)  # performance, revenue, optimization, system
    severity = Column(String, nullable=False)  # info, warning, critical, emergency
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    
    # Context and data
    alert_data = Column(JSON, default={})
    affected_components = Column(JSON, default={})
    trigger_conditions = Column(JSON, default={})
    
    # Actions
    recommended_actions = Column(JSON, default={})
    auto_actions_taken = Column(JSON, default={})
    manual_actions_required = Column(Boolean, default=False)
    
    # Status
    status = Column(String, default="new")  # new, acknowledged, resolved, dismissed
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Escalation
    escalation_level = Column(Integer, default=0)
    escalated_to = Column(String, nullable=True)
    escalation_reason = Column(Text, nullable=True)

class AIConfiguration(BaseModel, TimestampMixin):
    """AI service configuration"""
    __tablename__ = "ai_configurations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Configuration details
    config_name = Column(String, nullable=False)
    config_type = Column(String, nullable=False)  # global, agent, model, optimization
    config_scope = Column(String, default="user")  # user, organization, global
    
    # Configuration data
    config_data = Column(JSON, nullable=False)
    default_values = Column(JSON, default={})
    validation_rules = Column(JSON, default={})
    
    # Status
    status = Column(String, default="active")  # active, inactive, deprecated
    is_default = Column(Boolean, default=False)
    
    # Version control
    version = Column(String, default="1.0.0")
    previous_version_id = Column(String, nullable=True)
    change_summary = Column(Text, nullable=True)
    
    # Usage tracking
    applied_to_agents = Column(JSON, default={})
    last_applied = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)

class AISystemMetric(BaseModel, TimestampMixin):
    """System-wide AI metrics"""
    __tablename__ = "ai_system_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Metric identification
    metric_name = Column(String, nullable=False, index=True)
    metric_category = Column(String, nullable=False)  # performance, resource, quality
    
    # Metric values
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String, nullable=True)
    aggregation_type = Column(String, nullable=False)  # avg, sum, count, min, max
    
    # Time context
    measurement_window = Column(String, nullable=False)  # 1m, 5m, 1h, 24h
    time_bucket = Column(DateTime, nullable=False, index=True)
    
    # Additional context
    tags = Column(JSON, default={})
    dimensions = Column(JSON, default={})
    metadata = Column(JSON, default={})

# Helper functions for model operations
def create_conversation_record(
    agent_id: str,
    user_id: str,
    input_message: str,
    generated_response: str,
    confidence_score: float,
    context: dict = None
) -> Conversation:
    """Create a new conversation record"""
    return Conversation(
        agent_id=agent_id,
        user_id=user_id,
        input_message=input_message,
        generated_response=generated_response,
        confidence_score=confidence_score,
        context=context or {},
        response_time_ms=250,  # Default response time
        optimization_applied=True
    )

def create_ai_insight(
    user_id: str,
    insight_type: str,
    title: str,
    description: str,
    impact_description: str,
    confidence: float,
    recommended_action: str,
    agent_id: str = None
) -> AIInsight:
    """Create a new AI insight"""
    return AIInsight(
        user_id=user_id,
        agent_id=agent_id,
        insight_type=insight_type,
        category="optimization",
        title=title,
        description=description,
        impact_description=impact_description,
        impact_score=confidence,
        confidence=confidence,
        recommended_action=recommended_action
    )

def create_optimization_task(
    user_id: str,
    task_name: str,
    agent_ids: list,
    optimization_config: dict
) -> OptimizationTask:
    """Create a new optimization task"""
    return OptimizationTask(
        user_id=user_id,
        task_type="batch" if len(agent_ids) > 1 else "single_agent",
        task_name=task_name,
        target_agents={"agent_ids": agent_ids},
        optimization_config=optimization_config,
        estimated_duration=len(agent_ids) * 300  # 5 minutes per agent
    )

def create_neural_network(
    user_id: str,
    name: str,
    network_type: str,
    description: str,
    layers: int,
    neurons: int,
    architecture_config: dict
) -> NeuralNetwork:
    """Create a new neural network record"""
    return NeuralNetwork(
        user_id=user_id,
        name=name,
        network_type=network_type,
        description=description,
        layers=layers,
        neurons=neurons,
        architecture_config=architecture_config,
        accuracy=85.0,  # Initial accuracy
        status="training"
    )