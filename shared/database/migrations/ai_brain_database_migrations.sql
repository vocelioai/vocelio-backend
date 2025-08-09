-- AI Brain Service Database Migrations
-- Create all necessary tables for AI Brain functionality

-- Migration 001: Core AI Conversations Table
CREATE TABLE IF NOT EXISTS ai_conversations (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    agent_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    
    -- Conversation data
    input_message TEXT NOT NULL,
    generated_response TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    
    -- Performance metrics
    confidence_score DECIMAL(5,4) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    response_time_ms INTEGER NOT NULL DEFAULT 250,
    optimization_applied BOOLEAN DEFAULT true,
    
    -- Analysis results
    sentiment_analysis JSONB DEFAULT '{}',
    intent_analysis JSONB DEFAULT '{}',
    context_analysis JSONB DEFAULT '{}',
    
    -- Feedback and learning
    feedback_score DECIMAL(3,1) CHECK (feedback_score >= 0 AND feedback_score <= 10),
    feedback_text TEXT,
    human_feedback JSONB DEFAULT '{}',
    
    -- Metadata
    model_version VARCHAR(50) DEFAULT 'gpt-4-turbo',
    optimization_level VARCHAR(20) DEFAULT 'high',
    session_id VARCHAR(36),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_conversations
CREATE INDEX IF NOT EXISTS idx_ai_conversations_agent_id ON ai_conversations(agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_user_id ON ai_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_created_at ON ai_conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_session_id ON ai_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_confidence ON ai_conversations(confidence_score);

-- Migration 002: AI Conversation Analysis Table
CREATE TABLE IF NOT EXISTS ai_conversation_analysis (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    conversation_id VARCHAR(36) REFERENCES ai_conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL,
    
    -- Analysis results
    sentiment_scores JSONB NOT NULL DEFAULT '{}',
    emotion_scores JSONB DEFAULT '{}',
    intent_classification JSONB NOT NULL DEFAULT '{}',
    entity_extraction JSONB DEFAULT '{}',
    
    -- Quality metrics
    clarity_score DECIMAL(5,4) NOT NULL DEFAULT 0.5,
    engagement_score DECIMAL(5,4) NOT NULL DEFAULT 0.5,
    persuasiveness_score DECIMAL(5,4) NOT NULL DEFAULT 0.5,
    
    -- Optimization insights
    optimization_opportunities JSONB DEFAULT '{}',
    improvement_suggestions JSONB DEFAULT '{}',
    predicted_outcome JSONB DEFAULT '{}',
    
    -- Performance tracking
    actual_outcome VARCHAR(50),
    outcome_confidence DECIMAL(5,4),
    success_probability DECIMAL(5,4),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_conversation_analysis
CREATE INDEX IF NOT EXISTS idx_ai_conversation_analysis_conversation_id ON ai_conversation_analysis(conversation_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversation_analysis_user_id ON ai_conversation_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversation_analysis_created_at ON ai_conversation_analysis(created_at);

-- Migration 003: AI Optimizations Table
CREATE TABLE IF NOT EXISTS ai_optimizations (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    agent_id VARCHAR(36),
    
    -- Optimization details
    optimization_type VARCHAR(50) NOT NULL, -- voice, timing, script, targeting
    optimization_category VARCHAR(50) NOT NULL, -- performance, revenue, engagement
    
    -- Configuration
    original_config JSONB NOT NULL DEFAULT '{}',
    optimized_config JSONB NOT NULL DEFAULT '{}',
    optimization_goals JSONB DEFAULT '{}',
    
    -- Results
    status VARCHAR(20) DEFAULT 'pending', -- pending, active, completed, failed
    confidence_score DECIMAL(5,4) NOT NULL,
    expected_impact JSONB DEFAULT '{}',
    actual_impact JSONB DEFAULT '{}',
    
    -- Performance tracking
    baseline_metrics JSONB DEFAULT '{}',
    current_metrics JSONB DEFAULT '{}',
    improvement_percentage DECIMAL(7,4),
    
    -- Metadata
    applied_at TIMESTAMP WITH TIME ZONE,
    reverted_at TIMESTAMP WITH TIME ZONE,
    auto_applied BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_optimizations
CREATE INDEX IF NOT EXISTS idx_ai_optimizations_user_id ON ai_optimizations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_optimizations_agent_id ON ai_optimizations(agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_optimizations_status ON ai_optimizations(status);
CREATE INDEX IF NOT EXISTS idx_ai_optimizations_type ON ai_optimizations(optimization_type);
CREATE INDEX IF NOT EXISTS idx_ai_optimizations_created_at ON ai_optimizations(created_at);

-- Migration 004: Neural Networks Table
CREATE TABLE IF NOT EXISTS ai_neural_networks (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    
    -- Network details
    name VARCHAR(100) NOT NULL,
    network_type VARCHAR(50) NOT NULL, -- transformer, cnn, rnn, bert, gpt
    description TEXT,
    
    -- Architecture
    layers INTEGER NOT NULL DEFAULT 10,
    neurons INTEGER NOT NULL DEFAULT 1000,
    parameters JSONB DEFAULT '{}',
    architecture_config JSONB NOT NULL DEFAULT '{}',
    
    -- Performance
    accuracy DECIMAL(5,2) NOT NULL DEFAULT 85.0 CHECK (accuracy >= 0 AND accuracy <= 100),
    precision DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    
    -- Status and deployment
    status VARCHAR(20) DEFAULT 'training', -- training, active, idle, failed
    deployment_status VARCHAR(20) DEFAULT 'development', -- development, staging, production
    version VARCHAR(20) DEFAULT '1.0.0',
    
    -- Training information
    training_data_size VARCHAR(20), -- "847TB"
    training_duration INTEGER, -- seconds
    last_trained TIMESTAMP WITH TIME ZONE,
    
    -- Resource usage
    memory_usage_mb INTEGER,
    cpu_usage_percent DECIMAL(5,2),
    gpu_usage_percent DECIMAL(5,2),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_neural_networks
CREATE INDEX IF NOT EXISTS idx_ai_neural_networks_user_id ON ai_neural_networks(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_neural_networks_name ON ai_neural_networks(name);
CREATE INDEX IF NOT EXISTS idx_ai_neural_networks_status ON ai_neural_networks(status);
CREATE INDEX IF NOT EXISTS idx_ai_neural_networks_type ON ai_neural_networks(network_type);
CREATE INDEX IF NOT EXISTS idx_ai_neural_networks_accuracy ON ai_neural_networks(accuracy);

-- Migration 005: Training Sessions Table
CREATE TABLE IF NOT EXISTS ai_training_sessions (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    network_id VARCHAR(36) REFERENCES ai_neural_networks(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL,
    
    -- Training configuration
    training_config JSONB NOT NULL DEFAULT '{}',
    hyperparameters JSONB NOT NULL DEFAULT '{}',
    dataset_info JSONB NOT NULL DEFAULT '{}',
    
    -- Progress tracking
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed, cancelled
    current_epoch INTEGER DEFAULT 0,
    total_epochs INTEGER NOT NULL DEFAULT 10,
    progress_percentage DECIMAL(5,2) DEFAULT 0.0,
    
    -- Performance metrics
    training_loss DECIMAL(10,8),
    validation_loss DECIMAL(10,8),
    accuracy DECIMAL(5,4),
    learning_rate DECIMAL(10,8),
    
    -- Results
    final_metrics JSONB DEFAULT '{}',
    model_artifacts JSONB DEFAULT '{}', -- Paths to saved models
    training_logs JSONB DEFAULT '{}',
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    estimated_completion TIMESTAMP WITH TIME ZONE,
    
    -- Resources
    compute_resources JSONB DEFAULT '{}',
    total_compute_cost DECIMAL(10,2),
    
    -- Error handling
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_training_sessions
CREATE INDEX IF NOT EXISTS idx_ai_training_sessions_network_id ON ai_training_sessions(network_id);
CREATE INDEX IF NOT EXISTS idx_ai_training_sessions_user_id ON ai_training_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_training_sessions_status ON ai_training_sessions(status);
CREATE INDEX IF NOT EXISTS idx_ai_training_sessions_created_at ON ai_training_sessions(created_at);

-- Migration 006: AI Insights Table
CREATE TABLE IF NOT EXISTS ai_insights (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    agent_id VARCHAR(36),
    
    -- Insight details
    insight_type VARCHAR(20) NOT NULL, -- critical, optimization, trend, prediction
    category VARCHAR(50) NOT NULL, -- performance, revenue, optimization, alert
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    
    -- Impact and confidence
    impact_description VARCHAR(200) NOT NULL,
    impact_score DECIMAL(5,2) NOT NULL CHECK (impact_score >= 0 AND impact_score <= 100),
    confidence DECIMAL(5,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    
    -- Actions
    recommended_action VARCHAR(200) NOT NULL,
    action_priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    action_complexity VARCHAR(20) DEFAULT 'simple', -- simple, moderate, complex
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'new', -- new, viewed, applied, dismissed, expired
    applied_at TIMESTAMP WITH TIME ZONE,
    applied_by VARCHAR(36),
    
    -- Results tracking
    expected_results JSONB DEFAULT '{}',
    actual_results JSONB DEFAULT '{}',
    success_metrics JSONB DEFAULT '{}',
    
    -- Metadata
    data_sources JSONB DEFAULT '{}',
    methodology VARCHAR(100),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_insights
CREATE INDEX IF NOT EXISTS idx_ai_insights_user_id ON ai_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_agent_id ON ai_insights(agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_type ON ai_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_ai_insights_status ON ai_insights(status);
CREATE INDEX IF NOT EXISTS idx_ai_insights_created_at ON ai_insights(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_insights_priority ON ai_insights(action_priority);

-- Migration 007: AI Performance Metrics Table
CREATE TABLE IF NOT EXISTS ai_performance_metrics (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    agent_id VARCHAR(36),
    
    -- Metric details
    metric_type VARCHAR(50) NOT NULL, -- accuracy, performance, optimization
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,8) NOT NULL,
    metric_unit VARCHAR(20),
    
    -- Context
    measurement_context JSONB DEFAULT '{}',
    time_period VARCHAR(10), -- 1h, 24h, 7d, 30d
    
    -- Comparison data
    baseline_value DECIMAL(15,8),
    target_value DECIMAL(15,8),
    improvement_percentage DECIMAL(7,4),
    
    -- Quality indicators
    data_quality_score DECIMAL(5,4),
    confidence_interval JSONB DEFAULT '{}',
    statistical_significance DECIMAL(5,4),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_performance_metrics
CREATE INDEX IF NOT EXISTS idx_ai_performance_metrics_user_id ON ai_performance_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_performance_metrics_agent_id ON ai_performance_metrics(agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_performance_metrics_type ON ai_performance_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_ai_performance_metrics_name ON ai_performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_ai_performance_metrics_created_at ON ai_performance_metrics(created_at);

-- Migration 008: Optimization Tasks Table
CREATE TABLE IF NOT EXISTS ai_optimization_tasks (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    
    -- Task details
    task_type VARCHAR(20) NOT NULL, -- single_agent, batch, global
    task_name VARCHAR(100) NOT NULL,
    task_description TEXT,
    
    -- Configuration
    target_agents JSONB DEFAULT '{}', -- List of agent IDs
    optimization_config JSONB NOT NULL DEFAULT '{}',
    constraints JSONB DEFAULT '{}',
    
    -- Execution
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed, cancelled
    progress_percentage DECIMAL(5,2) DEFAULT 0.0,
    
    -- Results
    execution_log JSONB DEFAULT '{}',
    results_summary JSONB DEFAULT '{}',
    performance_impact JSONB DEFAULT '{}',
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    estimated_duration INTEGER, -- seconds
    
    -- Error handling
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_optimization_tasks
CREATE INDEX IF NOT EXISTS idx_ai_optimization_tasks_user_id ON ai_optimization_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_optimization_tasks_status ON ai_optimization_tasks(status);
CREATE INDEX IF NOT EXISTS idx_ai_optimization_tasks_type ON ai_optimization_tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_ai_optimization_tasks_created_at ON ai_optimization_tasks(created_at);

-- Migration 009: AI Alerts Table
CREATE TABLE IF NOT EXISTS ai_alerts (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36),
    agent_id VARCHAR(36),
    
    -- Alert details
    alert_type VARCHAR(50) NOT NULL, -- performance, revenue, optimization, system
    severity VARCHAR(20) NOT NULL, -- info, warning, critical, emergency
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    
    -- Context and data
    alert_data JSONB DEFAULT '{}',
    affected_components JSONB DEFAULT '{}',
    trigger_conditions JSONB DEFAULT '{}',
    
    -- Actions
    recommended_actions JSONB DEFAULT '{}',
    auto_actions_taken JSONB DEFAULT '{}',
    manual_actions_required BOOLEAN DEFAULT false,
    
    -- Status
    status VARCHAR(20) DEFAULT 'new', -- new, acknowledged, resolved, dismissed
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by VARCHAR(36),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    
    -- Escalation
    escalation_level INTEGER DEFAULT 0,
    escalated_to VARCHAR(36),
    escalation_reason TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_alerts
CREATE INDEX IF NOT EXISTS idx_ai_alerts_user_id ON ai_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_alerts_agent_id ON ai_alerts(agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_alerts_type ON ai_alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_ai_alerts_severity ON ai_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_ai_alerts_status ON ai_alerts(status);
CREATE INDEX IF NOT EXISTS idx_ai_alerts_created_at ON ai_alerts(created_at);

-- Migration 010: AI System Metrics Table
CREATE TABLE IF NOT EXISTS ai_system_metrics (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    
    -- Metric identification
    metric_name VARCHAR(100) NOT NULL,
    metric_category VARCHAR(50) NOT NULL, -- performance, resource, quality
    
    -- Metric values
    metric_value DECIMAL(15,8) NOT NULL,
    metric_unit VARCHAR(20),
    aggregation_type VARCHAR(20) NOT NULL, -- avg, sum, count, min, max
    
    -- Time context
    measurement_window VARCHAR(10) NOT NULL, -- 1m, 5m, 1h, 24h
    time_bucket TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Additional context
    tags JSONB DEFAULT '{}',
    dimensions JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_system_metrics
CREATE INDEX IF NOT EXISTS idx_ai_system_metrics_name ON ai_system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_ai_system_metrics_category ON ai_system_metrics(metric_category);
CREATE INDEX IF NOT EXISTS idx_ai_system_metrics_time_bucket ON ai_system_metrics(time_bucket);
CREATE INDEX IF NOT EXISTS idx_ai_system_metrics_window ON ai_system_metrics(measurement_window);

-- Unique constraint for time-series data
CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_system_metrics_unique 
ON ai_system_metrics(metric_name, time_bucket, measurement_window);

-- Migration 011: AI Learning Events Table
CREATE TABLE IF NOT EXISTS ai_learning_events (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    agent_id VARCHAR(36),
    conversation_id VARCHAR(36) REFERENCES ai_conversations(id) ON DELETE SET NULL,
    
    -- Event details
    event_type VARCHAR(50) NOT NULL, -- feedback, outcome, optimization
    event_source VARCHAR(20) NOT NULL, -- human, system, automated
    
    -- Learning data
    input_data JSONB NOT NULL DEFAULT '{}',
    expected_output JSONB,
    actual_output JSONB,
    
    -- Quality assessment
    quality_score DECIMAL(5,4),
    relevance_score DECIMAL(5,4),
    novelty_score DECIMAL(5,4),
    
    -- Learning impact
    model_update_applied BOOLEAN DEFAULT false,
    improvement_measured JSONB DEFAULT '{}',
    learning_weight DECIMAL(5,4) DEFAULT 1.0,
    
    -- Processing status
    processed BOOLEAN DEFAULT false,
    processing_results JSONB DEFAULT '{}',
    processing_errors JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_learning_events
CREATE INDEX IF NOT EXISTS idx_ai_learning_events_user_id ON ai_learning_events(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_learning_events_agent_id ON ai_learning_events(agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_learning_events_conversation_id ON ai_learning_events(conversation_id);
CREATE INDEX IF NOT EXISTS idx_ai_learning_events_type ON ai_learning_events(event_type);
CREATE INDEX IF NOT EXISTS idx_ai_learning_events_processed ON ai_learning_events(processed);
CREATE INDEX IF NOT EXISTS idx_ai_learning_events_created_at ON ai_learning_events(created_at);

-- Migration 012: AI Predictions Table
CREATE TABLE IF NOT EXISTS ai_predictions (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    agent_id VARCHAR(36),
    model_name VARCHAR(100),
    
    -- Prediction details
    prediction_type VARCHAR(50) NOT NULL, -- revenue, outcome, performance, timing
    input_features JSONB NOT NULL DEFAULT '{}',
    prediction_result JSONB NOT NULL DEFAULT '{}',
    
    -- Confidence and quality
    confidence_score DECIMAL(5,4) NOT NULL,
    uncertainty_range JSONB,
    prediction_horizon VARCHAR(10), -- 1d, 7d, 30d, 90d
    
    -- Validation
    actual_outcome JSONB,
    accuracy_score DECIMAL(5,4),
    prediction_error DECIMAL(10,8),
    
    -- Context
    market_conditions JSONB DEFAULT '{}',
    external_factors JSONB DEFAULT '{}',
    prediction_context JSONB DEFAULT '{}',
    
    -- Lifecycle
    expires_at TIMESTAMP WITH TIME ZONE,
    validated_at TIMESTAMP WITH TIME ZONE,
    invalidated_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_predictions
CREATE INDEX IF NOT EXISTS idx_ai_predictions_user_id ON ai_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_agent_id ON ai_predictions(agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_type ON ai_predictions(prediction_type);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_model ON ai_predictions(model_name);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_created_at ON ai_predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_expires_at ON ai_predictions(expires_at);

-- Migration 013: AI Configuration Table
CREATE TABLE IF NOT EXISTS ai_configurations (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    
    -- Configuration details
    config_name VARCHAR(100) NOT NULL,
    config_type VARCHAR(50) NOT NULL, -- global, agent, model, optimization
    config_scope VARCHAR(20) DEFAULT 'user', -- user, organization, global
    
    -- Configuration data
    config_data JSONB NOT NULL DEFAULT '{}',
    default_values JSONB DEFAULT '{}',
    validation_rules JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, deprecated
    is_default BOOLEAN DEFAULT false,
    
    -- Version control
    version VARCHAR(20) DEFAULT '1.0.0',
    previous_version_id VARCHAR(36),
    change_summary TEXT,
    
    -- Usage tracking
    applied_to_agents JSONB DEFAULT '{}',
    last_applied TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_configurations
CREATE INDEX IF NOT EXISTS idx_ai_configurations_user_id ON ai_configurations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_configurations_name ON ai_configurations(config_name);
CREATE INDEX IF NOT EXISTS idx_ai_configurations_type ON ai_configurations(config_type);
CREATE INDEX IF NOT EXISTS idx_ai_configurations_status ON ai_configurations(status);

-- Migration 014: AI Training Schedules Table (for automatic retraining)
CREATE TABLE IF NOT EXISTS ai_training_schedules (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    
    -- Schedule configuration
    trigger_conditions JSONB NOT NULL DEFAULT '{}',
    schedule_config JSONB DEFAULT '{}',
    training_config JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, paused, completed, failed
    next_execution TIMESTAMP WITH TIME ZONE,
    last_execution TIMESTAMP WITH TIME ZONE,
    
    -- Results tracking
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    last_result JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_training_schedules
CREATE INDEX IF NOT EXISTS idx_ai_training_schedules_user_id ON ai_training_schedules(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_training_schedules_model ON ai_training_schedules(model_name);
CREATE INDEX IF NOT EXISTS idx_ai_training_schedules_status ON ai_training_schedules(status);
CREATE INDEX IF NOT EXISTS idx_ai_training_schedules_next_execution ON ai_training_schedules(next_execution);

-- Migration 015: AI Sentiment Analysis Table (detailed sentiment tracking)
CREATE TABLE IF NOT EXISTS ai_sentiment_analysis (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    conversation_id VARCHAR(36) REFERENCES ai_conversations(id) ON DELETE CASCADE,
    
    -- Analysis details
    text_analyzed TEXT NOT NULL,
    text_index INTEGER,
    context VARCHAR(200),
    
    -- Sentiment results
    sentiment VARCHAR(20) NOT NULL, -- positive, negative, neutral
    confidence DECIMAL(5,4) NOT NULL,
    sentiment_scores JSONB NOT NULL DEFAULT '{}',
    emotions JSONB DEFAULT '{}',
    
    -- Additional analysis
    subjectivity DECIMAL(5,4),
    intensity DECIMAL(5,4),
    emotional_stability DECIMAL(5,4),
    
    -- Quality metrics
    analysis_quality DECIMAL(5,4),
    data_completeness DECIMAL(5,4),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ai_sentiment_analysis
CREATE INDEX IF NOT EXISTS idx_ai_sentiment_analysis_user_id ON ai_sentiment_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_sentiment_analysis_conversation_id ON ai_sentiment_analysis(conversation_id);
CREATE INDEX IF NOT EXISTS idx_ai_sentiment_analysis_sentiment ON ai_sentiment_analysis(sentiment);
CREATE INDEX IF NOT EXISTS idx_ai_sentiment_analysis_created_at ON ai_sentiment_analysis(created_at);

-- Create update triggers for all tables
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$ language 'plpgsql';

-- Apply update triggers to all relevant tables
CREATE TRIGGER update_ai_conversations_updated_at BEFORE UPDATE ON ai_conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_conversation_analysis_updated_at BEFORE UPDATE ON ai_conversation_analysis FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_optimizations_updated_at BEFORE UPDATE ON ai_optimizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_neural_networks_updated_at BEFORE UPDATE ON ai_neural_networks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_training_sessions_updated_at BEFORE UPDATE ON ai_training_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_insights_updated_at BEFORE UPDATE ON ai_insights FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_performance_metrics_updated_at BEFORE UPDATE ON ai_performance_metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_optimization_tasks_updated_at BEFORE UPDATE ON ai_optimization_tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_alerts_updated_at BEFORE UPDATE ON ai_alerts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_configurations_updated_at BEFORE UPDATE ON ai_configurations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_training_schedules_updated_at BEFORE UPDATE ON ai_training_schedules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_learning_events_updated_at BEFORE UPDATE ON ai_learning_events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_predictions_updated_at BEFORE UPDATE ON ai_predictions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for development/testing
INSERT INTO ai_neural_networks (user_id, name, network_type, description, layers, neurons, accuracy, status, training_data_size) VALUES
('system', 'Conversation Optimizer', 'Deep Learning', 'Real-time conversation flow optimization', 156, 2847392, 97.3, 'active', '847TB'),
('system', 'Voice Emotion Detector', 'Neural Network', 'Advanced sentiment and emotion analysis', 89, 1239847, 94.8, 'active', '234TB'),
('system', 'Outcome Predictor', 'Transformer', 'Call outcome prediction with 95% accuracy', 234, 3847291, 91.7, 'training', '1.2PB'),
('system', 'Timing Optimizer', 'Reinforcement Learning', 'Optimal call timing across global time zones', 67, 847392, 96.2, 'active', '456TB')
ON CONFLICT DO NOTHING;

-- Insert sample AI insights for demonstration
INSERT INTO ai_insights (user_id, insight_type, category, title, description, impact_description, impact_score, confidence, recommended_action) VALUES
('demo_user', 'critical', 'revenue', '🚨 Ultra High-Value Prospect Alert', 'AI detected 2,847 prospects with 95%+ booking probability', '$47M potential revenue', 95.0, 98.7, 'Priority dialing recommended'),
('demo_user', 'optimization', 'performance', '⚡ Performance Boost Available', 'Switch 89% of Solar campaigns to "Confident Mike" voice', '+34% success rate, +$2.3M revenue', 85.0, 97.2, 'Auto-apply optimization'),
('demo_user', 'trend', 'performance', '📈 Market Pattern Discovery', 'Peak performance window: 2:00-4:00 PM EST globally', '+67% answer rate improvement', 75.0, 94.1, 'Schedule smart timing'),
('demo_user', 'prediction', 'revenue', '🔮 Revenue Forecast Update', 'AI predicts 23% increase in Q4 conversions', '$12.7M additional projected revenue', 80.0, 91.8, 'Expand capacity planning')
ON CONFLICT DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW ai_dashboard_metrics AS
SELECT 
    user_id,
    COUNT(DISTINCT agent_id) as active_agents,
    COUNT(*) as total_conversations,
    AVG(confidence_score) as avg_confidence,
    AVG(response_time_ms) as avg_response_time,
    COUNT(*) FILTER (WHERE optimization_applied = true) as optimized_conversations,
    COUNT(*) FILTER (WHERE feedback_score IS NOT NULL) as conversations_with_feedback,
    AVG(feedback_score) as avg_feedback_score
FROM ai_conversations
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY user_id;

CREATE OR REPLACE VIEW ai_optimization_summary AS
SELECT 
    user_id,
    optimization_type,
    COUNT(*) as total_optimizations,
    COUNT(*) FILTER (WHERE status = 'active') as active_optimizations,
    AVG(confidence_score) as avg_confidence,
    AVG(improvement_percentage) as avg_improvement
FROM ai_optimizations
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY user_id, optimization_type;

-- Performance optimization: Partitioning for large tables (if needed in production)
-- This would be applied based on data volume and query patterns

-- Grant appropriate permissions
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_brain_service;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ai_brain_service;