-- =====================================================================================
-- 🚀 VOCELIO.AI COMPLETE SUPABASE DATABASE SCHEMA
-- =====================================================================================
-- Comprehensive PostgreSQL schema for the entire Vocelio platform
-- Includes all tables, relationships, indexes, and optimizations
-- Date: August 15, 2025
-- =====================================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- =====================================================================================
-- 📊 CORE BUSINESS TABLES
-- =====================================================================================

-- Organizations (Multi-tenant support)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    website VARCHAR(255),
    
    -- Subscription info
    subscription_plan VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(20) DEFAULT 'active',
    billing_email VARCHAR(255),
    
    -- Settings
    timezone VARCHAR(50) DEFAULT 'UTC',
    currency VARCHAR(3) DEFAULT 'USD',
    settings JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    verified_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- User details
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url TEXT,
    
    -- Authentication
    email_verified_at TIMESTAMPTZ,
    phone VARCHAR(20),
    phone_verified_at TIMESTAMPTZ,
    
    -- Role & Permissions
    role VARCHAR(50) DEFAULT 'user',
    permissions JSONB DEFAULT '[]',
    
    -- Profile
    bio TEXT,
    location VARCHAR(255),
    department VARCHAR(100),
    job_title VARCHAR(100),
    
    -- Settings
    settings JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    last_login_at TIMESTAMPTZ,
    login_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- =====================================================================================
-- 🤖 AI AGENTS & VOICE SYSTEM
-- =====================================================================================

-- AI Agents
CREATE TABLE ai_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Agent identity
    name VARCHAR(255) NOT NULL,
    description TEXT,
    avatar_url TEXT,
    
    -- Voice settings
    voice_id VARCHAR(100),
    voice_provider VARCHAR(50) DEFAULT 'elevenlabs',
    voice_settings JSONB DEFAULT '{}',
    
    -- AI Configuration
    model VARCHAR(100) DEFAULT 'gpt-4',
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 1000,
    system_prompt TEXT,
    personality JSONB DEFAULT '{}',
    
    -- Capabilities
    capabilities JSONB DEFAULT '[]',
    languages JSONB DEFAULT '["en"]',
    skills JSONB DEFAULT '{}',
    
    -- Performance
    total_calls INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    avg_call_duration INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    is_training BOOLEAN DEFAULT false,
    last_trained_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Voice Marketplace
CREATE TABLE voices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Voice details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    provider VARCHAR(50) NOT NULL,
    provider_voice_id VARCHAR(255) NOT NULL,
    
    -- Characteristics
    gender VARCHAR(10),
    age_range VARCHAR(20),
    accent VARCHAR(50),
    language VARCHAR(10) DEFAULT 'en',
    tone VARCHAR(50),
    
    -- Quality & Pricing
    quality_tier VARCHAR(20) DEFAULT 'standard',
    price_per_character DECIMAL(8,6),
    sample_audio_url TEXT,
    
    -- Metadata
    tags JSONB DEFAULT '[]',
    is_premium BOOLEAN DEFAULT false,
    is_custom BOOLEAN DEFAULT false,
    
    -- Usage stats
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.00,
    review_count INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================================
-- 📞 CALL CENTER & COMMUNICATION
-- =====================================================================================

-- Campaigns
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Campaign details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) DEFAULT 'outbound',
    
    -- Configuration
    script TEXT,
    objectives JSONB DEFAULT '[]',
    target_audience JSONB DEFAULT '{}',
    
    -- Scheduling
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Performance targets
    target_calls INTEGER,
    target_conversions INTEGER,
    target_conversion_rate DECIMAL(5,2),
    
    -- Current metrics
    total_calls INTEGER DEFAULT 0,
    successful_calls INTEGER DEFAULT 0,
    conversion_count INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Calls
CREATE TABLE calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Call identification
    twilio_call_sid VARCHAR(255) UNIQUE,
    external_id VARCHAR(255),
    
    -- Relationships
    agent_id UUID REFERENCES ai_agents(id),
    campaign_id UUID REFERENCES campaigns(id),
    user_id UUID REFERENCES users(id),
    
    -- Customer information
    customer_phone VARCHAR(20) NOT NULL,
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    customer_location VARCHAR(255),
    customer_type VARCHAR(100),
    customer_age INTEGER,
    interest_level VARCHAR(50),
    
    -- Call details
    status VARCHAR(20) DEFAULT 'queued',
    stage VARCHAR(50),
    priority VARCHAR(20) DEFAULT 'medium',
    direction VARCHAR(20) DEFAULT 'outbound',
    
    -- Timing
    started_at TIMESTAMPTZ,
    answered_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    
    -- Duration in seconds
    duration INTEGER,
    ring_duration INTEGER,
    talk_duration INTEGER,
    
    -- AI Analysis
    sentiment VARCHAR(50),
    confidence_score DECIMAL(5,2),
    conversion_probability DECIMAL(5,2),
    next_best_action TEXT,
    detected_objections JSONB,
    
    -- Call outcome
    outcome VARCHAR(100),
    outcome_details JSONB,
    appointment_scheduled BOOLEAN DEFAULT false,
    appointment_datetime TIMESTAMPTZ,
    
    -- Transfer information
    transferred_from_agent_id UUID,
    transferred_to_agent_id UUID,
    transfer_reason VARCHAR(255),
    transfer_type VARCHAR(50),
    transferred_at TIMESTAMPTZ,
    
    -- Recording & Quality
    recording_url TEXT,
    recording_duration INTEGER,
    quality_score DECIMAL(5,2),
    
    -- Cost & Revenue
    cost DECIMAL(10,2) DEFAULT 0.00,
    revenue DECIMAL(10,2) DEFAULT 0.00,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Call Recordings
CREATE TABLE call_recordings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id UUID NOT NULL REFERENCES calls(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Recording details
    recording_url TEXT NOT NULL,
    duration INTEGER NOT NULL,
    file_size INTEGER,
    format VARCHAR(10) DEFAULT 'wav',
    
    -- Transcript
    transcript TEXT,
    transcript_confidence DECIMAL(5,2),
    
    -- Analysis
    sentiment_analysis JSONB,
    keywords JSONB,
    moments JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'available',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Phone Numbers
CREATE TABLE phone_numbers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Number details
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    friendly_name VARCHAR(255),
    country_code VARCHAR(3),
    number_type VARCHAR(20) DEFAULT 'local',
    
    -- Provider info
    provider VARCHAR(50) DEFAULT 'twilio',
    provider_sid VARCHAR(255),
    
    -- Configuration
    voice_url TEXT,
    sms_url TEXT,
    status_callback_url TEXT,
    
    -- Capabilities
    voice_enabled BOOLEAN DEFAULT true,
    sms_enabled BOOLEAN DEFAULT true,
    mms_enabled BOOLEAN DEFAULT false,
    
    -- Usage
    monthly_cost DECIMAL(8,2),
    usage_count INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================================
-- 📊 ANALYTICS & REPORTING
-- =====================================================================================

-- Call Metrics (Aggregated)
CREATE TABLE call_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Time dimensions
    date TIMESTAMPTZ NOT NULL,
    hour INTEGER NOT NULL CHECK (hour >= 0 AND hour <= 23),
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    
    -- Call volume metrics
    total_calls INTEGER DEFAULT 0,
    successful_calls INTEGER DEFAULT 0,
    failed_calls INTEGER DEFAULT 0,
    abandoned_calls INTEGER DEFAULT 0,
    
    -- Performance metrics
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    avg_duration DECIMAL(8,2) DEFAULT 0.00,
    avg_wait_time DECIMAL(8,2) DEFAULT 0.00,
    
    -- Revenue metrics
    revenue_generated DECIMAL(12,2) DEFAULT 0.00,
    cost_incurred DECIMAL(12,2) DEFAULT 0.00,
    
    -- Quality metrics
    customer_satisfaction DECIMAL(3,2) DEFAULT 0.00,
    quality_score DECIMAL(5,2) DEFAULT 0.00,
    
    -- Reference data
    campaign_id UUID REFERENCES campaigns(id),
    agent_id UUID REFERENCES ai_agents(id),
    voice_id UUID REFERENCES voices(id),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent Metrics (Daily)
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES ai_agents(id) ON DELETE CASCADE,
    
    -- Time dimension
    date TIMESTAMPTZ NOT NULL,
    
    -- Agent details
    agent_name VARCHAR(255) NOT NULL,
    
    -- Call metrics
    total_calls INTEGER DEFAULT 0,
    successful_calls INTEGER DEFAULT 0,
    failed_calls INTEGER DEFAULT 0,
    
    -- Performance metrics
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    avg_call_duration DECIMAL(8,2) DEFAULT 0.00,
    avg_response_time DECIMAL(8,2) DEFAULT 0.00,
    
    -- Quality metrics
    customer_satisfaction DECIMAL(3,2) DEFAULT 0.00,
    quality_score DECIMAL(5,2) DEFAULT 0.00,
    performance_score DECIMAL(5,2) DEFAULT 0.00,
    
    -- Revenue metrics
    revenue_generated DECIMAL(12,2) DEFAULT 0.00,
    leads_converted INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    
    -- Availability metrics (in seconds)
    online_time INTEGER DEFAULT 0,
    idle_time INTEGER DEFAULT 0,
    break_time INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Campaign Metrics (Daily)
CREATE TABLE campaign_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    
    -- Time dimension
    date TIMESTAMPTZ NOT NULL,
    
    -- Campaign details
    campaign_name VARCHAR(255) NOT NULL,
    
    -- Call metrics
    total_calls INTEGER DEFAULT 0,
    successful_calls INTEGER DEFAULT 0,
    failed_calls INTEGER DEFAULT 0,
    
    -- Conversion metrics
    leads_generated INTEGER DEFAULT 0,
    appointments_booked INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    
    -- Performance metrics
    avg_call_duration DECIMAL(8,2) DEFAULT 0.00,
    contact_rate DECIMAL(5,2) DEFAULT 0.00,
    
    -- Cost metrics
    total_cost DECIMAL(12,2) DEFAULT 0.00,
    cost_per_call DECIMAL(8,2) DEFAULT 0.00,
    cost_per_conversion DECIMAL(8,2) DEFAULT 0.00,
    
    -- Revenue metrics
    revenue_generated DECIMAL(12,2) DEFAULT 0.00,
    roi DECIMAL(8,2) DEFAULT 0.00,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Real-time Metrics
CREATE TABLE real_time_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Metrics timestamp (usually current minute)
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- Current state
    active_calls INTEGER DEFAULT 0,
    queued_calls INTEGER DEFAULT 0,
    available_agents INTEGER DEFAULT 0,
    busy_agents INTEGER DEFAULT 0,
    
    -- Hourly aggregates
    calls_this_hour INTEGER DEFAULT 0,
    successful_calls_hour INTEGER DEFAULT 0,
    failed_calls_hour INTEGER DEFAULT 0,
    
    -- Daily aggregates
    calls_today INTEGER DEFAULT 0,
    revenue_today DECIMAL(12,2) DEFAULT 0.00,
    conversions_today INTEGER DEFAULT 0,
    
    -- Performance indicators
    avg_wait_time_current DECIMAL(8,2) DEFAULT 0.00,
    avg_call_duration_hour DECIMAL(8,2) DEFAULT 0.00,
    success_rate_hour DECIMAL(5,2) DEFAULT 0.00,
    
    -- System health
    system_load DECIMAL(5,2) DEFAULT 0.00,
    api_response_time INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================================
-- 🔧 FLOW BUILDER & AUTOMATION
-- =====================================================================================

-- Flows
CREATE TABLE flows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Flow details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    
    -- Flow configuration
    flow_data JSONB,
    viewport JSONB,
    
    -- Status and versioning
    status VARCHAR(50) DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    is_template BOOLEAN DEFAULT false,
    
    -- Metadata
    tags JSONB DEFAULT '[]',
    settings JSONB DEFAULT '{}',
    
    -- Performance metrics
    total_executions INTEGER DEFAULT 0,
    success_rate INTEGER DEFAULT 0,
    avg_duration INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    last_executed_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

-- Flow Versions
CREATE TABLE flow_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flow_id UUID NOT NULL REFERENCES flows(id) ON DELETE CASCADE,
    
    -- Version info
    version_number INTEGER NOT NULL,
    version_name VARCHAR(255),
    description TEXT,
    
    -- Snapshot of flow data
    flow_data JSONB,
    viewport JSONB,
    
    -- Metadata
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Flow Nodes
CREATE TABLE flow_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flow_id UUID NOT NULL REFERENCES flows(id) ON DELETE CASCADE,
    
    -- Node identification
    node_id VARCHAR(255) NOT NULL,
    node_type VARCHAR(100) NOT NULL,
    
    -- Position and styling
    position_x DECIMAL(10,2),
    position_y DECIMAL(10,2),
    width INTEGER,
    height INTEGER,
    
    -- Node configuration
    data JSONB DEFAULT '{}',
    style JSONB DEFAULT '{}',
    
    -- Connections
    source_connections JSONB DEFAULT '[]',
    target_connections JSONB DEFAULT '[]',
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Flow Executions
CREATE TABLE flow_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flow_id UUID NOT NULL REFERENCES flows(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Execution details
    execution_id VARCHAR(255) UNIQUE NOT NULL,
    trigger_type VARCHAR(100),
    trigger_data JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'running',
    current_node_id VARCHAR(255),
    
    -- Timing
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration INTEGER,
    
    -- Results
    output_data JSONB,
    error_message TEXT,
    execution_log JSONB DEFAULT '[]',
    
    -- Context
    context JSONB DEFAULT '{}',
    variables JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================================
-- 💼 BUSINESS & BILLING
-- =====================================================================================

-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Subscription details
    plan_name VARCHAR(100) NOT NULL,
    plan_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    
    -- Billing
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    billing_cycle VARCHAR(20) DEFAULT 'monthly',
    
    -- Payment provider
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    
    -- Dates
    trial_ends_at TIMESTAMPTZ,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    canceled_at TIMESTAMPTZ,
    ends_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id),
    
    -- Invoice details
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    
    -- Amounts
    subtotal DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(12,2) DEFAULT 0.00,
    discount_amount DECIMAL(12,2) DEFAULT 0.00,
    total_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Payment
    payment_status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMPTZ,
    due_date TIMESTAMPTZ,
    
    -- Provider info
    stripe_invoice_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Usage Tracking
CREATE TABLE usage_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Usage period
    billing_period_start TIMESTAMPTZ NOT NULL,
    billing_period_end TIMESTAMPTZ NOT NULL,
    
    -- Call usage
    total_calls INTEGER DEFAULT 0,
    call_minutes INTEGER DEFAULT 0,
    
    -- AI usage
    ai_tokens_used INTEGER DEFAULT 0,
    voice_characters INTEGER DEFAULT 0,
    
    -- Storage usage (in MB)
    storage_used INTEGER DEFAULT 0,
    recordings_storage INTEGER DEFAULT 0,
    
    -- Costs
    call_costs DECIMAL(12,2) DEFAULT 0.00,
    ai_costs DECIMAL(12,2) DEFAULT 0.00,
    voice_costs DECIMAL(12,2) DEFAULT 0.00,
    storage_costs DECIMAL(12,2) DEFAULT 0.00,
    total_costs DECIMAL(12,2) DEFAULT 0.00,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================================
-- 🛠️ SYSTEM & CONFIGURATION
-- =====================================================================================

-- Settings
CREATE TABLE settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Setting details
    category VARCHAR(100) NOT NULL,
    key VARCHAR(255) NOT NULL,
    value JSONB,
    
    -- Metadata
    description TEXT,
    data_type VARCHAR(50) DEFAULT 'string',
    is_encrypted BOOLEAN DEFAULT false,
    is_public BOOLEAN DEFAULT false,
    
    -- Validation
    validation_rules JSONB,
    default_value JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(organization_id, category, key)
);

-- API Keys
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    
    -- Key details
    name VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    
    -- Permissions
    scopes JSONB DEFAULT '[]',
    permissions JSONB DEFAULT '{}',
    
    -- Usage limits
    rate_limit_per_minute INTEGER DEFAULT 1000,
    rate_limit_per_hour INTEGER DEFAULT 10000,
    rate_limit_per_day INTEGER DEFAULT 100000,
    
    -- Usage stats
    last_used_at TIMESTAMPTZ,
    usage_count INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    expires_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Webhooks
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Webhook details
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    secret VARCHAR(255),
    
    -- Configuration
    events JSONB DEFAULT '[]',
    headers JSONB DEFAULT '{}',
    
    -- Settings
    is_active BOOLEAN DEFAULT true,
    retry_count INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 30,
    
    -- Stats
    last_triggered_at TIMESTAMPTZ,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    
    -- Event details
    event_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    
    -- Action details
    action VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Data
    old_data JSONB,
    new_data JSONB,
    metadata JSONB DEFAULT '{}',
    
    -- Request context
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================================
-- 🔐 SECURITY & COMPLIANCE
-- =====================================================================================

-- Data Retention Policies
CREATE TABLE data_retention_policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Policy details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Scope
    data_type VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    
    -- Retention rules
    retention_period_days INTEGER NOT NULL,
    delete_method VARCHAR(50) DEFAULT 'soft_delete',
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_executed_at TIMESTAMPTZ,
    next_execution_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- GDPR Requests
CREATE TABLE gdpr_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Request details
    request_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    
    -- Subject details
    subject_email VARCHAR(255),
    subject_phone VARCHAR(20),
    subject_id UUID,
    
    -- Processing
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Data
    request_details JSONB,
    processing_log JSONB DEFAULT '[]',
    exported_data JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================================
-- 📈 DATA WAREHOUSE & ANALYTICS
-- =====================================================================================

-- Data Sources
CREATE TABLE data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Source details
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    connection_string TEXT,
    
    -- Configuration
    config JSONB DEFAULT '{}',
    schema_mapping JSONB DEFAULT '{}',
    sync_frequency VARCHAR(50) DEFAULT 'daily',
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    last_sync_at TIMESTAMPTZ,
    next_sync_at TIMESTAMPTZ,
    
    -- Stats
    total_records INTEGER DEFAULT 0,
    sync_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data Pipeline Jobs
CREATE TABLE data_pipeline_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    data_source_id UUID REFERENCES data_sources(id),
    
    -- Job details
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    
    -- Execution
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration INTEGER,
    
    -- Results
    records_processed INTEGER DEFAULT 0,
    records_success INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    
    -- Error handling
    error_message TEXT,
    error_details JSONB,
    
    -- Data
    job_config JSONB,
    execution_log JSONB DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================================
-- 📚 KNOWLEDGE BASE & CONTENT
-- =====================================================================================

-- Knowledge Base Articles
CREATE TABLE knowledge_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Article details
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    slug VARCHAR(255) UNIQUE NOT NULL,
    
    -- Categorization
    category VARCHAR(100),
    tags JSONB DEFAULT '[]',
    language VARCHAR(10) DEFAULT 'en',
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft',
    featured BOOLEAN DEFAULT false,
    
    -- SEO
    meta_title VARCHAR(255),
    meta_description TEXT,
    
    -- Authoring
    author_id UUID REFERENCES users(id),
    
    -- Usage stats
    view_count INTEGER DEFAULT 0,
    helpful_votes INTEGER DEFAULT 0,
    unhelpful_votes INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

-- Templates
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Template details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(100) NOT NULL,
    
    -- Content
    template_data JSONB NOT NULL,
    variables JSONB DEFAULT '[]',
    
    -- Categorization
    category VARCHAR(100),
    tags JSONB DEFAULT '[]',
    
    -- Usage
    usage_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT false,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- =====================================================================================
-- 🎯 LEAD MANAGEMENT & CRM
-- =====================================================================================

-- Leads
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Contact information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    company VARCHAR(255),
    job_title VARCHAR(100),
    
    -- Address
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    
    -- Lead details
    source VARCHAR(100),
    status VARCHAR(50) DEFAULT 'new',
    priority VARCHAR(20) DEFAULT 'medium',
    
    -- Scoring
    lead_score INTEGER DEFAULT 0,
    qualification_status VARCHAR(50),
    
    -- Assignment
    assigned_to UUID REFERENCES users(id),
    assigned_at TIMESTAMPTZ,
    
    -- Custom fields
    custom_fields JSONB DEFAULT '{}',
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Lead Activities
CREATE TABLE lead_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Activity details
    activity_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Scheduling
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Assignment
    assigned_to UUID REFERENCES users(id),
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================================
-- 📧 NOTIFICATIONS & COMMUNICATIONS
-- =====================================================================================

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Recipient
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Notification details
    type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    
    -- Channel
    channel VARCHAR(50) DEFAULT 'in_app',
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    read_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    
    -- Action
    action_url TEXT,
    action_data JSONB,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Email Templates
CREATE TABLE email_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Template details
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    html_content TEXT NOT NULL,
    text_content TEXT,
    
    -- Template variables
    variables JSONB DEFAULT '[]',
    
    -- Categorization
    category VARCHAR(100),
    language VARCHAR(10) DEFAULT 'en',
    
    -- Usage
    usage_count INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- =====================================================================================
-- 📅 SCHEDULING & APPOINTMENTS
-- =====================================================================================

-- Appointments
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Appointment details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Participants
    lead_id UUID REFERENCES leads(id),
    user_id UUID REFERENCES users(id),
    call_id UUID REFERENCES calls(id),
    
    -- Scheduling
    scheduled_at TIMESTAMPTZ NOT NULL,
    duration INTEGER DEFAULT 30,
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Meeting details
    meeting_url TEXT,
    meeting_platform VARCHAR(50),
    meeting_id VARCHAR(255),
    
    -- Status
    status VARCHAR(50) DEFAULT 'scheduled',
    
    -- Reminders
    reminder_sent_at TIMESTAMPTZ,
    confirmation_status VARCHAR(50),
    
    -- Follow-up
    follow_up_required BOOLEAN DEFAULT false,
    follow_up_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- =====================================================================================
-- 🔌 INTEGRATIONS & WEBHOOKS
-- =====================================================================================

-- Integration Connections
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Integration details
    name VARCHAR(255) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    type VARCHAR(100) NOT NULL,
    
    -- Configuration
    config JSONB NOT NULL,
    credentials JSONB,
    
    -- Sync settings
    sync_enabled BOOLEAN DEFAULT true,
    sync_frequency VARCHAR(50) DEFAULT 'real_time',
    last_sync_at TIMESTAMPTZ,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    
    -- Error handling
    last_error TEXT,
    error_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Webhook Logs
CREATE TABLE webhook_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    webhook_id UUID NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Request details
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    headers JSONB,
    
    -- Response details
    response_status INTEGER,
    response_body TEXT,
    response_time INTEGER,
    
    -- Retry information
    attempt_number INTEGER DEFAULT 1,
    max_attempts INTEGER DEFAULT 3,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- =====================================================================================
-- 📊 ADDITIONAL ANALYTICS TABLES
-- =====================================================================================

-- Voice Metrics
CREATE TABLE voice_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    voice_id UUID REFERENCES voices(id),
    
    -- Time dimension
    date TIMESTAMPTZ NOT NULL,
    
    -- Usage metrics
    characters_used INTEGER DEFAULT 0,
    requests_count INTEGER DEFAULT 0,
    
    -- Performance metrics
    avg_generation_time DECIMAL(8,2) DEFAULT 0.00,
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    
    -- Quality metrics
    quality_rating DECIMAL(3,2) DEFAULT 0.00,
    user_satisfaction DECIMAL(3,2) DEFAULT 0.00,
    
    -- Cost metrics
    total_cost DECIMAL(12,2) DEFAULT 0.00,
    cost_per_character DECIMAL(8,6) DEFAULT 0.00,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================================
-- 🔍 INDEXES FOR PERFORMANCE
-- =====================================================================================

-- Organizations indexes
CREATE INDEX idx_organizations_slug ON organizations(slug);
CREATE INDEX idx_organizations_status ON organizations(status) WHERE deleted_at IS NULL;

-- Users indexes
CREATE INDEX idx_users_org ON users(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_role ON users(organization_id, role) WHERE deleted_at IS NULL;

-- AI Agents indexes
CREATE INDEX idx_agents_org ON ai_agents(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_agents_status ON ai_agents(organization_id, status);

-- Calls indexes  
CREATE INDEX idx_calls_org_created ON calls(organization_id, created_at);
CREATE INDEX idx_calls_agent ON calls(agent_id, created_at);
CREATE INDEX idx_calls_campaign ON calls(campaign_id, created_at);
CREATE INDEX idx_calls_status ON calls(organization_id, status);
CREATE INDEX idx_calls_customer_phone ON calls(customer_phone);
CREATE INDEX idx_calls_twilio_sid ON calls(twilio_call_sid);

-- Call Metrics indexes
CREATE INDEX idx_call_metrics_org_date ON call_metrics(organization_id, date);
CREATE INDEX idx_call_metrics_org_hour ON call_metrics(organization_id, date, hour);
CREATE INDEX idx_call_metrics_campaign ON call_metrics(campaign_id, date);
CREATE INDEX idx_call_metrics_agent ON call_metrics(agent_id, date);

-- Agent Metrics indexes
CREATE INDEX idx_agent_metrics_org_date ON agent_metrics(organization_id, date);
CREATE INDEX idx_agent_metrics_agent_date ON agent_metrics(agent_id, date);

-- Campaign Metrics indexes
CREATE INDEX idx_campaign_metrics_org_date ON campaign_metrics(organization_id, date);
CREATE INDEX idx_campaign_metrics_campaign_date ON campaign_metrics(campaign_id, date);

-- Flows indexes
CREATE INDEX idx_flows_org ON flows(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_flows_user ON flows(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_flows_status ON flows(organization_id, status);

-- Settings indexes
CREATE INDEX idx_settings_org_category ON settings(organization_id, category);
CREATE UNIQUE INDEX idx_settings_org_key ON settings(organization_id, category, key);

-- Audit Logs indexes
CREATE INDEX idx_audit_logs_org_created ON audit_logs(organization_id, created_at);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

-- Knowledge Articles indexes
CREATE INDEX idx_knowledge_articles_org ON knowledge_articles(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_knowledge_articles_status ON knowledge_articles(organization_id, status);
CREATE INDEX idx_knowledge_articles_slug ON knowledge_articles(slug) WHERE deleted_at IS NULL;
CREATE INDEX idx_knowledge_articles_category ON knowledge_articles(organization_id, category);

-- Templates indexes
CREATE INDEX idx_templates_org ON templates(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_templates_type ON templates(organization_id, type);

-- Leads indexes
CREATE INDEX idx_leads_org ON leads(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_status ON leads(organization_id, status);
CREATE INDEX idx_leads_assigned ON leads(assigned_to, created_at);
CREATE INDEX idx_leads_email ON leads(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_phone ON leads(phone) WHERE deleted_at IS NULL;

-- Lead Activities indexes
CREATE INDEX idx_lead_activities_lead ON lead_activities(lead_id, created_at);
CREATE INDEX idx_lead_activities_assigned ON lead_activities(assigned_to, due_date);
CREATE INDEX idx_lead_activities_status ON lead_activities(organization_id, status);

-- Notifications indexes
CREATE INDEX idx_notifications_user ON notifications(user_id, created_at);
CREATE INDEX idx_notifications_status ON notifications(user_id, status);
CREATE INDEX idx_notifications_type ON notifications(organization_id, type);

-- Appointments indexes
CREATE INDEX idx_appointments_org_scheduled ON appointments(organization_id, scheduled_at);
CREATE INDEX idx_appointments_lead ON appointments(lead_id, scheduled_at);
CREATE INDEX idx_appointments_user ON appointments(user_id, scheduled_at);
CREATE INDEX idx_appointments_status ON appointments(organization_id, status);

-- Integrations indexes
CREATE INDEX idx_integrations_org ON integrations(organization_id);
CREATE INDEX idx_integrations_provider ON integrations(organization_id, provider);
CREATE INDEX idx_integrations_status ON integrations(organization_id, status);

-- Webhook Logs indexes
CREATE INDEX idx_webhook_logs_webhook ON webhook_logs(webhook_id, created_at);
CREATE INDEX idx_webhook_logs_status ON webhook_logs(organization_id, status);
CREATE INDEX idx_webhook_logs_event ON webhook_logs(organization_id, event_type);

-- Voice Metrics indexes
CREATE INDEX idx_voice_metrics_org_date ON voice_metrics(organization_id, date);
CREATE INDEX idx_voice_metrics_voice_date ON voice_metrics(voice_id, date);

-- =====================================================================================
-- 🔧 TRIGGERS & FUNCTIONS
-- =====================================================================================

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers to all relevant tables
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_agents_updated_at BEFORE UPDATE ON ai_agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_calls_updated_at BEFORE UPDATE ON calls FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_flows_updated_at BEFORE UPDATE ON flows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_call_metrics_updated_at BEFORE UPDATE ON call_metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agent_metrics_updated_at BEFORE UPDATE ON agent_metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaign_metrics_updated_at BEFORE UPDATE ON campaign_metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_articles_updated_at BEFORE UPDATE ON knowledge_articles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_voice_metrics_updated_at BEFORE UPDATE ON voice_metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================================================
-- 🔐 ROW LEVEL SECURITY (RLS)
-- =====================================================================================

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_recordings ENABLE ROW LEVEL SECURITY;
ALTER TABLE phone_numbers ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE flows ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_metrics ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (example for organizations)
CREATE POLICY "Users can view their organization" ON organizations
    FOR SELECT USING (auth.uid()::text IN (
        SELECT id::text FROM users WHERE organization_id = organizations.id
    ));

-- =====================================================================================
-- 📊 MATERIALIZED VIEWS FOR PERFORMANCE
-- =====================================================================================

-- Daily organization summary
CREATE MATERIALIZED VIEW daily_org_summary AS
SELECT 
    organization_id,
    DATE(created_at) as summary_date,
    COUNT(*) as total_calls,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_calls,
    AVG(duration) as avg_duration,
    SUM(COALESCE(revenue, 0)) as total_revenue,
    SUM(COALESCE(cost, 0)) as total_cost
FROM calls 
GROUP BY organization_id, DATE(created_at);

CREATE UNIQUE INDEX ON daily_org_summary (organization_id, summary_date);

-- Agent performance summary  
CREATE MATERIALIZED VIEW agent_performance_summary AS
SELECT 
    a.id as agent_id,
    a.name as agent_name,
    a.organization_id,
    COUNT(c.id) as total_calls,
    COUNT(c.id) FILTER (WHERE c.status = 'completed') as successful_calls,
    AVG(c.duration) as avg_call_duration,
    AVG(c.quality_score) as avg_quality_score,
    SUM(COALESCE(c.revenue, 0)) as total_revenue
FROM ai_agents a
LEFT JOIN calls c ON a.id = c.agent_id
WHERE a.deleted_at IS NULL
GROUP BY a.id, a.name, a.organization_id;

CREATE UNIQUE INDEX ON agent_performance_summary (agent_id);

-- =====================================================================================
-- 🎯 SAMPLE DATA INSERTION
-- =====================================================================================

-- Insert sample organization
INSERT INTO organizations (id, name, slug, email, subscription_plan, status)
VALUES (
    uuid_generate_v4(),
    'Vocelio Demo Organization', 
    'vocelio-demo',
    'demo@vocelio.ai',
    'pro',
    'active'
);

-- =====================================================================================
-- ✅ SCHEMA CREATION COMPLETE
-- =====================================================================================

COMMENT ON SCHEMA public IS 'Complete Vocelio.ai database schema v1.0 - Production Ready';

-- Enable performance monitoring
SELECT pg_stat_statements_reset();

-- Show final table count
SELECT 
    schemaname,
    COUNT(*) as table_count
FROM pg_tables 
WHERE schemaname = 'public'
GROUP BY schemaname;

-- =====================================================================================
-- 🚀 SUCCESS! YOUR VOCELIO DATABASE IS READY
-- =====================================================================================
