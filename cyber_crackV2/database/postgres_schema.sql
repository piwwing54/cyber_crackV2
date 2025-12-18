-- CYBER CRACK PRO - PostgreSQL Schema
-- Database schema for storing analysis results, user data, and job information

-- Create the cybercrackpro database (run this separately if needed)
-- CREATE DATABASE cybercrackpro;

-- Connect to the database before running these commands
-- \c cybercrackpro;

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table for users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    api_key VARCHAR(255),
    quota_monthly INTEGER DEFAULT 100,
    quota_used INTEGER DEFAULT 0,
    role VARCHAR(50) DEFAULT 'user'
);

-- Table for job submissions
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    job_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id VARCHAR(50) REFERENCES users(user_id),
    apk_name VARCHAR(255) NOT NULL,
    apk_hash VARCHAR(64), -- SHA-256 hash
    apk_size BIGINT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Table for analysis results
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    security_score INTEGER,
    vulnerabilities JSONB,
    protections JSONB,
    recommendations JSONB,
    detailed_results JSONB,
    engines_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for processing results
CREATE TABLE processing_results (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    mode VARCHAR(100),
    modified_apk_path VARCHAR(500),
    fixes_applied TEXT[],
    stability_score INTEGER,
    success BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for APK metadata
CREATE TABLE apk_metadata (
    id SERIAL PRIMARY KEY,
    apk_hash VARCHAR(64) UNIQUE NOT NULL,
    package_name VARCHAR(255),
    app_name VARCHAR(255),
    version_name VARCHAR(50),
    version_code INTEGER,
    min_sdk_version INTEGER,
    target_sdk_version INTEGER,
    permissions JSONB,
    activities JSONB,
    services JSONB,
    receivers JSONB,
    providers JSONB,
    libraries JSONB,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for crack patterns and knowledge base
CREATE TABLE crack_patterns (
    id SERIAL PRIMARY KEY,
    pattern_name VARCHAR(255) UNIQUE NOT NULL,
    pattern_type VARCHAR(100),
    pattern_regex TEXT,
    description TEXT,
    severity VARCHAR(20),
    applicable_to TEXT[],
    patch_template TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for user quotas and usage
CREATE TABLE user_usage (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    job_id UUID REFERENCES jobs(job_id),
    quota_type VARCHAR(50),
    usage_count INTEGER DEFAULT 1,
    usage_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for system statistics
CREATE TABLE system_stats (
    id SERIAL PRIMARY KEY,
    stat_date DATE DEFAULT CURRENT_DATE,
    total_jobs INTEGER DEFAULT 0,
    successful_jobs INTEGER DEFAULT 0,
    failed_jobs INTEGER DEFAULT 0,
    total_analysis INTEGER DEFAULT 0,
    avg_processing_time INTERVAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_apk_hash ON jobs(apk_hash);
CREATE INDEX idx_analysis_job_id ON analysis_results(job_id);
CREATE INDEX idx_processing_job_id ON processing_results(job_id);
CREATE INDEX idx_apk_metadata_hash ON apk_metadata(apk_hash);
CREATE INDEX idx_crack_patterns_type ON crack_patterns(pattern_type);
CREATE INDEX idx_user_usage_user_id ON user_usage(user_id);
CREATE INDEX idx_user_usage_date ON user_usage(usage_date);

-- Insert default crack patterns
INSERT INTO crack_patterns (pattern_name, pattern_type, pattern_regex, description, severity, applicable_to, patch_template) VALUES
('Certificate Pinning', 'regex', 'checkServerTrusted|X509TrustManager|SSLSocketFactory', 'Certificate pinning implementation', 'MEDIUM', '{network,security}', 'cert_pinning_bypass'),
('Root Detection', 'regex', 'isRooted|rootbeer|root check|superuser', 'Root detection implementation', 'MEDIUM', '{security,utility}', 'root_detection_bypass'),
('Anti-Debug', 'regex', 'isDebuggerConnected|debugger|jdwp', 'Anti-debugging implementation', 'MEDIUM', '{security,banking}', 'anti_debug_bypass'),
('Hardcoded API Key', 'regex', 'api[_-]?key|token|secret', 'Hardcoded API key in code', 'CRITICAL', '{all}', 'remove_hardcoded_creds'),
('In-App Purchase', 'regex', 'billing|purchase|receipt|verify', 'In-app purchase verification logic', 'HIGH', '{game,utility,media}', 'iap_bypass'),
('Login Authentication', 'regex', 'login|authenticate|auth|session', 'Login/authentication verification', 'HIGH', '{social,finance,utility}', 'auth_bypass');

-- Insert default user if needed
INSERT INTO users (user_id, username, email, role) VALUES
('default_user', 'Default User', 'user@example.com', 'user')
ON CONFLICT (user_id) DO NOTHING;

-- Function to update job status
CREATE OR REPLACE FUNCTION update_job_status()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Update user quota when a new job is inserted
        UPDATE users 
        SET quota_used = quota_used + 1 
        WHERE user_id = NEW.user_id;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Update completed_at when status changes to completed
        IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
            NEW.completed_at = CURRENT_TIMESTAMP;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger for job updates
CREATE TRIGGER trigger_job_updates
    BEFORE INSERT OR UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_job_status();

-- Function to update timestamps on analysis update
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for analysis results updates
CREATE TRIGGER trigger_analysis_update
    BEFORE UPDATE ON analysis_results
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- View to get job statistics
CREATE VIEW job_stats AS
SELECT 
    DATE_TRUNC('day', created_at) as day,
    COUNT(*) as total_jobs,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_jobs,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_jobs,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))/60) as avg_processing_minutes
FROM jobs 
WHERE created_at > CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at')
ORDER BY day DESC;

-- Create function for getting user's remaining quota
CREATE OR REPLACE FUNCTION get_user_remaining_quota(p_user_id VARCHAR(50))
RETURNS INTEGER AS $$
DECLARE
    v_quota_total INTEGER;
    v_quota_used INTEGER;
BEGIN
    SELECT quota_monthly, quota_used 
    INTO v_quota_total, v_quota_used
    FROM users 
    WHERE user_id = p_user_id;
    
    IF v_quota_total IS NULL THEN
        RETURN 0;
    END IF;
    
    RETURN GREATEST(0, v_quota_total - COALESCE(v_quota_used, 0));
END;
$$ LANGUAGE plpgsql;