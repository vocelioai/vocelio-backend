-- apps/team-hub/src/database/migrations/001_initial_team_hub.sql

-- Create organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100) UNIQUE,
    logo_url VARCHAR(500),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    address TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create index on organizations
CREATE INDEX IF NOT EXISTS idx_organizations_domain ON organizations(domain);
CREATE INDEX IF NOT EXISTS idx_organizations_active ON organizations(is_active);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    organization_id VARCHAR(255) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    avatar VARCHAR(10) DEFAULT '👤',
    role VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'offline' CHECK (status IN ('online', 'on-call', 'break', 'training', 'offline')),
    last_login TIMESTAMP WITH TIME ZONE,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    location VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    performance_score DECIMAL(5,2) DEFAULT 0.0 CHECK (performance_score >= 0 AND performance_score <= 100),
    calls_today INTEGER DEFAULT 0 CHECK (calls_today >= 0),
    avg_call_duration INTEGER DEFAULT 0 CHECK (avg_call_duration >= 0),
    customer_satisfaction DECIMAL(5,2) DEFAULT 0.0 CHECK (customer_satisfaction >= 0 AND customer_satisfaction <= 100),
    skills JSONB DEFAULT '[]',
    certifications JSONB DEFAULT '[]',
    join_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes on users
CREATE INDEX IF NOT EXISTS idx_users_organization ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_department ON users(department);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_performance ON users(performance_score);
CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity);

-- Create teams table
CREATE TABLE IF NOT EXISTS teams (
    id VARCHAR(255) PRIMARY KEY,
    organization_id VARCHAR(255) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    department VARCHAR(100) NOT NULL,
    team_lead_id VARCHAR(255) REFERENCES users(id) ON DELETE SET NULL,
    performance_score DECIMAL(5,2) DEFAULT 0.0 CHECK (performance_score >= 0 AND performance_score <= 100),
    total_calls_today INTEGER DEFAULT 0 CHECK (total_calls_today >= 0),
    avg_satisfaction DECIMAL(5,2) DEFAULT 0.0 CHECK (avg_satisfaction >= 0 AND avg_satisfaction <= 100),
    member_count INTEGER DEFAULT 0 CHECK (member_count >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes on teams
CREATE INDEX IF NOT EXISTS idx_teams_organization ON teams(organization_id);
CREATE INDEX IF NOT EXISTS idx_teams_department ON teams(department);
CREATE INDEX IF NOT EXISTS idx_teams_lead ON teams(team_lead_id);
CREATE INDEX IF NOT EXISTS idx_teams_active ON teams(is_active);
CREATE INDEX IF NOT EXISTS idx_teams_performance ON teams(performance_score);

-- Create team_memberships table
CREATE TABLE IF NOT EXISTS team_memberships (
    id VARCHAR(255) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_in_team VARCHAR(100),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(team_id, user_id)
);

-- Create indexes on team_memberships
CREATE INDEX IF NOT EXISTS idx_memberships_team ON team_memberships(team_id);
CREATE INDEX IF NOT EXISTS idx_memberships_user ON team_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_memberships_active ON team_memberships(is_active);

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
    id VARCHAR(255) PRIMARY KEY,
    organization_id VARCHAR(255) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(organization_id, name)
);

-- Create indexes on roles
CREATE INDEX IF NOT EXISTS idx_roles_organization ON roles(organization_id);
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);
CREATE INDEX IF NOT EXISTS idx_roles_active ON roles(is_active);

-- Create invitations table
CREATE TABLE IF NOT EXISTS invitations (
    id VARCHAR(255) PRIMARY KEY,
    organization_id VARCHAR(255) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    invited_by_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined', 'expired')),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    accepted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes on invitations
CREATE INDEX IF NOT EXISTS idx_invitations_organization ON invitations(organization_id);
CREATE INDEX IF NOT EXISTS idx_invitations_email ON invitations(email);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON invitations(status);
CREATE INDEX IF NOT EXISTS idx_invitations_expires ON invitations(expires_at);
CREATE INDEX IF NOT EXISTS idx_invitations_invited_by ON invitations(invited_by_id);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invitations_updated_at BEFORE UPDATE ON invitations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default roles for new organizations
INSERT INTO roles (id, organization_id, name, description, permissions) VALUES
('role_admin_default', 'org_default', 'Admin', 'Full system administrator', 
 '["admin:full_access", "user:create", "user:read", "user:update", "user:delete", "team:create", "team:read", "team:update", "team:delete", "team:manage_members", "team:manage_leadership", "role:create", "role:read", "role:update", "role:delete", "invitation:create", "invitation:read", "invitation:delete", "invitation:resend", "dashboard:view_analytics", "dashboard:export_reports"]'),

('role_manager_default', 'org_default', 'Manager', 'Team manager with user management capabilities',
 '["user:read", "user:update", "team:read", "team:update", "team:manage_members", "invitation:create", "invitation:read", "dashboard:view_analytics"]'),

('role_user_default', 'org_default', 'User', 'Standard user with basic access',
 '["user:read", "team:read", "dashboard:view_analytics"]');

-- Create sample data (for development/testing)
-- This would be removed in production or moved to a separate seed file

-- Sample organization
INSERT INTO organizations (id, name, domain, contact_email, timezone) VALUES
('org_sample_001', 'Vocelio Demo Organization', 'demo.vocelio.ai', 'admin@demo.vocelio.ai', 'UTC')
ON CONFLICT (id) DO NOTHING;

-- Sample users
INSERT INTO users (id, organization_id, name, email, role, department, status, performance_score, calls_today, customer_satisfaction, location, skills, certifications) VALUES
('usr_001', 'org_sample_001', 'Sarah Chen', 'sarah.chen@demo.vocelio.ai', 'Senior AI Agent Manager', 'Operations', 'online', 98.5, 73, 98.2, 'San Francisco, CA', '["Team Leadership", "AI Optimization", "Customer Success"]', '["TCPA Advanced", "AI Agent Specialist", "Leadership Pro"]'),
('usr_002', 'org_sample_001', 'Marcus Rodriguez', 'marcus.rodriguez@demo.vocelio.ai', 'AI Call Specialist', 'Sales', 'on-call', 95.8, 89, 94.7, 'Austin, TX', '["Sales Excellence", "Lead Conversion", "CRM Management"]', '["Sales Pro", "AI Voice Specialist"]'),
('usr_003', 'org_sample_001', 'Elena Vasquez', 'elena.vasquez@demo.vocelio.ai', 'Compliance Specialist', 'Legal & Compliance', 'training', 99.1, 0, 97.9, 'Miami, FL', '["TCPA Compliance", "Legal Review", "Risk Management"]', '["TCPA Expert", "GDPR Specialist", "Compliance Master"]'),
('usr_004', 'org_sample_001', 'David Kim', 'david.kim@demo.vocelio.ai', 'Technical Support Lead', 'Technology', 'break', 92.4, 45, 91.8, 'Seattle, WA', '["Technical Support", "System Integration", "API Management"]', '["Technical Expert", "API Specialist"]'),
('usr_005', 'org_sample_001', 'Amanda Foster', 'amanda.foster@demo.vocelio.ai', 'Quality Assurance Manager', 'Quality', 'offline', 96.7, 0, 95.4, 'Denver, CO', '["Quality Control", "Performance Analysis", "Training Development"]', '["QA Professional", "Training Specialist"]'),
('usr_006', 'org_sample_001', 'James Wilson', 'james.wilson@demo.vocelio.ai', 'Customer Success Representative', 'Customer Success', 'online', 93.9, 67, 96.1, 'Chicago, IL', '["Customer Relations", "Account Management", "Retention Strategy"]', '["Customer Success Pro", "Account Management"]')
ON CONFLICT (id) DO NOTHING;

-- Sample teams
INSERT INTO teams (id, organization_id, name, description, department, team_lead_id, performance_score, total_calls_today, avg_satisfaction, member_count) VALUES
('team_001', 'org_sample_001', 'Operations Alpha', 'Primary operations team handling high-volume campaigns', 'Operations', 'usr_001', 96.8, 250, 97.1, 12),
('team_002', 'org_sample_001', 'Sales Force One', 'Elite sales team focusing on enterprise clients', 'Sales', 'usr_002', 94.2, 180, 95.5, 8),
('team_003', 'org_sample_001', 'Compliance Shield', 'Dedicated compliance and legal review team', 'Legal & Compliance', 'usr_003', 98.5, 45, 98.8, 5)
ON CONFLICT (id) DO NOTHING;

-- Sample team memberships
INSERT INTO team_memberships (id, team_id, user_id, role_in_team) VALUES
('tmem_001', 'team_001', 'usr_001', 'Team Lead'),
('tmem_002', 'team_002', 'usr_002', 'Team Lead'), 
('tmem_003', 'team_003', 'usr_003', 'Team Lead'),
('tmem_004', 'team_001', 'usr_006', 'Senior Member'),
('tmem_005', 'team_001', 'usr_004', 'Technical Support')
ON CONFLICT (team_id, user_id) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW team_performance_summary AS
SELECT 
    t.id as team_id,
    t.name as team_name,
    t.department,
    t.member_count,
    t.performance_score as team_performance,
    COUNT(u.id) as active_members,
    AVG(u.performance_score) as avg_member_performance,
    SUM(u.calls_today) as total_calls_today,
    AVG(u.customer_satisfaction) as avg_satisfaction
FROM teams t
LEFT JOIN team_memberships tm ON t.id = tm.team_id AND tm.is_active = true
LEFT JOIN users u ON tm.user_id = u.id AND u.is_active = true
WHERE t.is_active = true
GROUP BY t.id, t.name, t.department, t.member_count, t.performance_score;

CREATE OR REPLACE VIEW department_summary AS
SELECT 
    u.department,
    u.organization_id,
    COUNT(*) as member_count,
    AVG(u.performance_score) as avg_performance,
    SUM(u.calls_today) as total_calls_today,
    AVG(u.customer_satisfaction) as avg_satisfaction,
    COUNT(CASE WHEN u.status = 'online' THEN 1 END) as online_count,
    COUNT(CASE WHEN u.status = 'on-call' THEN 1 END) as on_call_count,
    COUNT(CASE WHEN u.status = 'break' THEN 1 END) as break_count,
    COUNT(CASE WHEN u.status = 'training' THEN 1 END) as training_count,
    COUNT(CASE WHEN u.status = 'offline' THEN 1 END) as offline_count
FROM users u
WHERE u.is_active = true
GROUP BY u.department, u.organization_id;

-- Grant necessary permissions
-- Note: In production, create specific database users with limited permissions
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO team_hub_service;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO team_hub_service;