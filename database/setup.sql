-- ScamShield AI Database Schema for Real Data
-- PostgreSQL database setup for production deployment

-- Create database
-- CREATE DATABASE scamshield_ai;

-- Use the database
-- \c scamshield_ai;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Threat Intelligence Table
CREATE TABLE threat_intelligence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    threat_type VARCHAR(50) NOT NULL,
    indicator_value TEXT NOT NULL,
    indicator_type VARCHAR(20) NOT NULL, -- ip, domain, url, hash, email
    confidence_score DECIMAL(3,2) NOT NULL,
    severity VARCHAR(10) NOT NULL, -- low, medium, high, critical
    source VARCHAR(100) NOT NULL,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tags TEXT[],
    metadata JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scan Results Table
CREATE TABLE scan_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id VARCHAR(100) UNIQUE NOT NULL,
    message_text TEXT NOT NULL,
    sender_info JSONB,
    risk_score DECIMAL(5,4) NOT NULL,
    classification VARCHAR(20) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    features JSONB NOT NULL,
    threat_indicators JSONB,
    processing_time_ms INTEGER,
    model_version VARCHAR(20),
    api_version VARCHAR(10),
    client_ip INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Real-time Metrics Table (for dashboard KPIs)
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_type VARCHAR(20) NOT NULL, -- counter, gauge, histogram
    tags JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Activity Log Table
CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    event_severity VARCHAR(10) NOT NULL, -- info, warning, error, critical
    event_message TEXT NOT NULL,
    event_details JSONB,
    source_component VARCHAR(50),
    user_id UUID,
    session_id VARCHAR(100),
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users Table (for enterprise features)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'analyst', -- admin, analyst, viewer
    organization VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API Keys Table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_name VARCHAR(100) NOT NULL,
    api_key_hash TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    permissions JSONB DEFAULT '{"scan": true, "stats": false, "admin": false}',
    rate_limit INTEGER DEFAULT 1000, -- requests per hour
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE
);

-- Geographic Data Table
CREATE TABLE geographic_threats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country_code CHAR(2) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    threat_count INTEGER DEFAULT 0,
    risk_level VARCHAR(10) DEFAULT 'low', -- low, medium, high, critical
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reports Table
CREATE TABLE generated_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_name VARCHAR(200) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    report_format VARCHAR(10) DEFAULT 'pdf',
    generated_by UUID REFERENCES users(id),
    report_data JSONB NOT NULL,
    file_path TEXT,
    file_size INTEGER,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'completed', -- pending, completed, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_threat_intelligence_type ON threat_intelligence(threat_type);
CREATE INDEX idx_threat_intelligence_indicator ON threat_intelligence(indicator_value);
CREATE INDEX idx_threat_intelligence_created ON threat_intelligence(created_at);

CREATE INDEX idx_scan_results_created ON scan_results(created_at);
CREATE INDEX idx_scan_results_classification ON scan_results(classification);
CREATE INDEX idx_scan_results_risk_score ON scan_results(risk_score);

CREATE INDEX idx_system_metrics_name_time ON system_metrics(metric_name, timestamp);
CREATE INDEX idx_activity_log_created ON activity_log(created_at);
CREATE INDEX idx_activity_log_severity ON activity_log(event_severity);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_api_keys_hash ON api_keys(api_key_hash);

-- Sample data for development
INSERT INTO users (username, email, password_hash, full_name, role, organization) VALUES
('admin', 'admin@elephasai.com', crypt('admin123', gen_salt('bf')), 'System Administrator', 'admin', 'Elephas AI'),
('analyst1', 'analyst@elephasai.com', crypt('analyst123', gen_salt('bf')), 'Security Analyst', 'analyst', 'Elephas AI'),
('viewer1', 'viewer@elephasai.com', crypt('viewer123', gen_salt('bf')), 'Security Viewer', 'viewer', 'Elephas AI');

-- Sample threat intelligence data
INSERT INTO threat_intelligence (threat_type, indicator_value, indicator_type, confidence_score, severity, source) VALUES
('phishing', 'malicious-site.com', 'domain', 0.95, 'high', 'PhishTank'),
('malware', '8.8.4.4', 'ip', 0.87, 'medium', 'VirusTotal'),
('spam', 'spam@fake-bank.com', 'email', 0.92, 'high', 'Internal'),
('fraud', 'crypto-scam.net', 'domain', 0.98, 'critical', 'URLVoid');

-- Sample geographic data
INSERT INTO geographic_threats (country_code, country_name, threat_count, risk_level, latitude, longitude) VALUES
('US', 'United States', 1247, 'medium', 39.8283, -98.5795),
('CN', 'China', 892, 'high', 35.8617, 104.1954),
('RU', 'Russia', 756, 'high', 61.5240, 105.3188),
('BR', 'Brazil', 234, 'medium', -14.2350, -51.9253),
('IN', 'India', 445, 'medium', 20.5937, 78.9629);

-- Trigger to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_threat_intelligence_updated_at BEFORE UPDATE ON threat_intelligence
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
