-- shared/database/migrations/001_phone_numbers_initial.sql
-- Initial schema for phone numbers service

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Phone Numbers table
CREATE TABLE phone_numbers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    twilio_sid VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(50) UNIQUE NOT NULL,
    friendly_name VARCHAR(100) NOT NULL,
    
    -- Organization/User association
    organization_id UUID NOT NULL,
    user_id UUID NOT NULL,
    
    -- Geographic information
    country_code VARCHAR(2) NOT NULL,
    region VARCHAR(100),
    locality VARCHAR(100),
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Number classification
    number_type VARCHAR(20) NOT NULL CHECK (number_type IN ('local', 'toll_free', 'mobile')),
    capabilities JSONB NOT NULL DEFAULT '["voice"]',
    
    -- Twilio configuration
    voice_url TEXT,
    voice_method VARCHAR(10) DEFAULT 'POST',
    voice_fallback_url TEXT,
    voice_fallback_method VARCHAR(10) DEFAULT 'POST',
    sms_url TEXT,
    sms_method VARCHAR(10) DEFAULT 'POST',
    sms_fallback_url TEXT,
    sms_fallback_method VARCHAR(10) DEFAULT 'POST',
    status_callback TEXT,
    status_callback_method VARCHAR(10) DEFAULT 'POST',
    
    -- Status and configuration
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'released', 'pending')),
    emergency_enabled BOOLEAN DEFAULT FALSE,
    emergency_address_sid VARCHAR(255),
    
    -- Billing information
    monthly_price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    billing_cycle_day INTEGER DEFAULT 1,
    
    -- Usage tracking
    total_calls INTEGER DEFAULT 0,
    total_minutes DECIMAL(12, 2) DEFAULT 0.0,
    total_sms INTEGER DEFAULT 0,
    total_mms INTEGER DEFAULT 0,
    
    -- Campaign associations
    campaign_count INTEGER DEFAULT 0,
    active_campaign_count INTEGER DEFAULT 0,
    
    -- Metadata
    tags JSONB,
    notes TEXT,
    custom_properties JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    purchased_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    released_at TIMESTAMP WITH TIME ZONE
);

-- Phone Number Verifications table
CREATE TABLE phone_number_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number_id UUID NOT NULL REFERENCES phone_numbers(id) ON DELETE CASCADE,
    
    -- Verification details
    verification_type VARCHAR(20) NOT NULL CHECK (verification_type IN ('ownership', 'compliance', 'carrier')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'verified', 'failed', 'expired')),
    verification_code VARCHAR(10),
    verification_method VARCHAR(20) CHECK (verification_method IN ('sms', 'voice', 'email')),
    
    -- Results
    verified_at TIMESTAMP WITH TIME ZONE,
    verification_data JSONB,
    error_message TEXT,
    
    -- Metadata
    requested_by UUID NOT NULL,
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Phone Number Purchases table
CREATE TABLE phone_number_purchases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number_id UUID REFERENCES phone_numbers(id) ON DELETE SET NULL,
    
    -- Purchase details
    organization_id UUID NOT NULL,
    user_id UUID NOT NULL,
    
    -- Pricing information
    base_price DECIMAL(10, 2) NOT NULL,
    setup_fee DECIMAL(10, 2) DEFAULT 0.0,
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Payment information
    stripe_payment_intent_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'succeeded', 'failed', 'refunded')),
    payment_method VARCHAR(50),
    
    -- Twilio information
    twilio_purchase_data JSONB,
    provisioning_status VARCHAR(20) DEFAULT 'pending' CHECK (provisioning_status IN ('pending', 'provisioned', 'failed')),
    provisioning_error TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    payment_completed_at TIMESTAMP WITH TIME ZONE,
    provisioned_at TIMESTAMP WITH TIME ZONE
);

-- Phone Number Usage table
CREATE TABLE phone_number_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number_id UUID NOT NULL REFERENCES phone_numbers(id) ON DELETE CASCADE,
    
    -- Usage period
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Call usage
    inbound_calls INTEGER DEFAULT 0,
    outbound_calls INTEGER DEFAULT 0,
    total_call_duration DECIMAL(12, 2) DEFAULT 0.0,
    
    -- Messaging usage
    inbound_sms INTEGER DEFAULT 0,
    outbound_sms INTEGER DEFAULT 0,
    inbound_mms INTEGER DEFAULT 0,
    outbound_mms INTEGER DEFAULT 0,
    
    -- Cost tracking
    call_costs DECIMAL(10, 4) DEFAULT 0.0,
    sms_costs DECIMAL(10, 4) DEFAULT 0.0,
    mms_costs DECIMAL(10, 4) DEFAULT 0.0,
    total_costs DECIMAL(10, 4) DEFAULT 0.0,
    
    -- Campaign tracking
    campaign_id UUID,
    campaign_name VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Number Porting table
CREATE TABLE number_porting (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number_id UUID REFERENCES phone_numbers(id) ON DELETE SET NULL,
    
    -- Porting details
    organization_id UUID NOT NULL,
    user_id UUID NOT NULL,
    
    external_phone_number VARCHAR(50) NOT NULL,
    current_carrier VARCHAR(100),
    account_number VARCHAR(50),
    pin_code VARCHAR(20),
    
    -- Porting status
    status VARCHAR(20) DEFAULT 'submitted' CHECK (status IN ('submitted', 'pending', 'approved', 'completed', 'failed')),
    twilio_porting_sid VARCHAR(255),
    
    -- Documentation
    documentation_url TEXT,
    rejection_reason TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    submitted_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX idx_phone_numbers_organization ON phone_numbers(organization_id);
CREATE INDEX idx_phone_numbers_user ON phone_numbers(user_id);
CREATE INDEX idx_phone_numbers_country_type ON phone_numbers(country_code, number_type);
CREATE INDEX idx_phone_numbers_status ON phone_numbers(status);
CREATE INDEX idx_phone_numbers_twilio_sid ON phone_numbers(twilio_sid);

CREATE INDEX idx_verifications_phone_number ON phone_number_verifications(phone_number_id);
CREATE INDEX idx_verifications_status ON phone_number_verifications(status);

CREATE INDEX idx_purchases_organization ON phone_number_purchases(organization_id);
CREATE INDEX idx_purchases_payment_status ON phone_number_purchases(payment_status);
CREATE INDEX idx_purchases_stripe_intent ON phone_number_purchases(stripe_payment_intent_id);

CREATE INDEX idx_usage_phone_number ON phone_number_usage(phone_number_id);
CREATE INDEX idx_usage_period ON phone_number_usage(period_start, period_end);
CREATE INDEX idx_usage_campaign ON phone_number_usage(campaign_id);

CREATE INDEX idx_porting_organization ON number_porting(organization_id);
CREATE INDEX idx_porting_status ON number_porting(status);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$ language 'plpgsql';

CREATE TRIGGER update_phone_numbers_updated_at 
    BEFORE UPDATE ON phone_numbers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_verifications_updated_at 
    BEFORE UPDATE ON phone_number_verifications 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_purchases_updated_at 
    BEFORE UPDATE ON phone_number_purchases 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usage_updated_at 
    BEFORE UPDATE ON phone_number_usage 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_porting_updated_at 
    BEFORE UPDATE ON number_porting 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for development
INSERT INTO phone_numbers (
    twilio_sid, phone_number, friendly_name, organization_id, user_id,
    country_code, region, locality, number_type, capabilities,
    monthly_price, status, purchased_at
) VALUES 
(
    'PN1234567890abcdef1234567890abcdef',
    '+15551234567',
    'Main Sales Line',
    '550e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440001',
    'US', 'CA', 'San Francisco', 'local', '["voice", "sms"]',
    1.15, 'active', NOW()
),
(
    'PN1234567890abcdef1234567890abcde2',
    '+18005551234',
    'Toll-Free Support',
    '550e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440001',
    'US', NULL, NULL, 'toll_free', '["voice"]',
    2.00, 'active', NOW()
);