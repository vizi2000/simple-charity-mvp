-- Database schema for charity payment system
-- Supports PostgreSQL/MySQL

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    contact_phone VARCHAR(50),
    contact_email VARCHAR(255),
    website VARCHAR(255),
    logo_url VARCHAR(500),
    primary_color VARCHAR(7),
    secondary_color VARCHAR(7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Goals table
CREATE TABLE IF NOT EXISTS goals (
    id VARCHAR(100) PRIMARY KEY,
    organization_id VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    target_amount DECIMAL(10, 2),
    collected_amount DECIMAL(10, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- Payments table with enhanced tracking
CREATE TABLE IF NOT EXISTS payments (
    payment_id UUID PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    organization_id VARCHAR(100) NOT NULL,
    goal_id VARCHAR(100),
    
    -- Payment details
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'PLN',
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, declined, failed, cancelled
    
    -- Donor information
    donor_name VARCHAR(255),
    donor_email VARCHAR(255),
    donor_phone VARCHAR(50),
    donor_message TEXT,
    is_anonymous BOOLEAN DEFAULT FALSE,
    
    -- Transaction details
    transaction_id VARCHAR(100), -- From Fiserv
    approval_code VARCHAR(50),
    payment_method VARCHAR(50), -- card, blik, transfer
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    txn_datetime VARCHAR(50), -- Fiserv format
    webhook_received_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Security and tracking
    client_ip VARCHAR(45),
    hash_used VARCHAR(100), -- First 20 chars of hash for debugging
    form_params_count INT,
    
    -- Error handling
    fail_reason TEXT,
    error_code VARCHAR(50),
    
    -- Indexes for performance
    INDEX idx_order_id (order_id),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_organization_goal (organization_id, goal_id),
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);

-- Webhook processing log for idempotency
CREATE TABLE IF NOT EXISTS webhook_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(100),
    transaction_id VARCHAR(100),
    status VARCHAR(50),
    webhook_type VARCHAR(50), -- s2s, redirect, manual
    
    -- Request details
    client_ip VARCHAR(45),
    request_headers TEXT,
    request_body TEXT,
    
    -- Processing
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    
    -- Response
    response_code INT,
    response_body TEXT,
    
    -- Timestamps
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    UNIQUE INDEX idx_order_transaction (order_id, transaction_id),
    INDEX idx_received_at (received_at),
    INDEX idx_processed (processed)
);

-- Rate limiting table
CREATE TABLE IF NOT EXISTS rate_limits (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    identifier VARCHAR(255) NOT NULL, -- IP:email or similar
    request_type VARCHAR(50), -- payment_init, webhook, status_check
    
    -- Tracking
    request_count INT DEFAULT 1,
    first_request_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_request_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Window tracking
    minute_window TIMESTAMP,
    minute_count INT DEFAULT 0,
    hour_window TIMESTAMP,
    hour_count INT DEFAULT 0,
    
    -- Blocking
    is_blocked BOOLEAN DEFAULT FALSE,
    blocked_until TIMESTAMP,
    block_reason TEXT,
    
    -- Indexes
    INDEX idx_identifier (identifier),
    INDEX idx_windows (minute_window, hour_window)
);

-- Audit log for all payment operations
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL, -- payment_created, status_changed, webhook_received
    entity_type VARCHAR(50), -- payment, webhook, goal
    entity_id VARCHAR(100),
    
    -- Change tracking
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(255), -- system, webhook, admin
    
    -- Context
    client_ip VARCHAR(45),
    user_agent TEXT,
    additional_data TEXT, -- JSON format
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_event_type (event_type),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_created_at (created_at)
);

-- Statistics table for reporting
CREATE TABLE IF NOT EXISTS payment_statistics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    organization_id VARCHAR(100),
    goal_id VARCHAR(100),
    
    -- Counts
    total_payments INT DEFAULT 0,
    approved_payments INT DEFAULT 0,
    declined_payments INT DEFAULT 0,
    failed_payments INT DEFAULT 0,
    
    -- Amounts
    total_amount DECIMAL(12, 2) DEFAULT 0,
    approved_amount DECIMAL(12, 2) DEFAULT 0,
    average_amount DECIMAL(10, 2) DEFAULT 0,
    
    -- Payment methods
    card_payments INT DEFAULT 0,
    blik_payments INT DEFAULT 0,
    transfer_payments INT DEFAULT 0,
    
    -- Performance
    avg_processing_time_seconds INT,
    webhook_success_rate DECIMAL(5, 2),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    UNIQUE INDEX idx_date_org_goal (date, organization_id, goal_id),
    INDEX idx_date (date),
    INDEX idx_organization (organization_id)
);

-- Views for reporting
CREATE OR REPLACE VIEW payment_summary AS
SELECT 
    p.organization_id,
    o.name as organization_name,
    g.name as goal_name,
    COUNT(*) as total_payments,
    SUM(CASE WHEN p.status = 'approved' THEN 1 ELSE 0 END) as approved_count,
    SUM(CASE WHEN p.status = 'approved' THEN p.amount ELSE 0 END) as total_revenue,
    AVG(CASE WHEN p.status = 'approved' THEN p.amount ELSE NULL END) as avg_payment,
    MAX(p.created_at) as last_payment_date
FROM payments p
LEFT JOIN organizations o ON p.organization_id = o.id
LEFT JOIN goals g ON p.goal_id = g.id
GROUP BY p.organization_id, o.name, g.name;

-- Stored procedures for common operations
DELIMITER //

CREATE PROCEDURE update_goal_collected_amount(IN p_goal_id VARCHAR(100))
BEGIN
    UPDATE goals g
    SET collected_amount = (
        SELECT COALESCE(SUM(amount), 0)
        FROM payments
        WHERE goal_id = p_goal_id
        AND status = 'approved'
    )
    WHERE g.id = p_goal_id;
END//

CREATE PROCEDURE check_rate_limit(
    IN p_identifier VARCHAR(255),
    IN p_max_per_minute INT,
    IN p_max_per_hour INT,
    OUT p_allowed BOOLEAN
)
BEGIN
    DECLARE v_minute_count INT;
    DECLARE v_hour_count INT;
    DECLARE v_current_time TIMESTAMP;
    
    SET v_current_time = NOW();
    
    -- Count requests in last minute
    SELECT COUNT(*) INTO v_minute_count
    FROM rate_limits
    WHERE identifier = p_identifier
    AND last_request_at >= DATE_SUB(v_current_time, INTERVAL 1 MINUTE);
    
    -- Count requests in last hour
    SELECT COUNT(*) INTO v_hour_count
    FROM rate_limits
    WHERE identifier = p_identifier
    AND last_request_at >= DATE_SUB(v_current_time, INTERVAL 1 HOUR);
    
    IF v_minute_count >= p_max_per_minute OR v_hour_count >= p_max_per_hour THEN
        SET p_allowed = FALSE;
    ELSE
        SET p_allowed = TRUE;
        -- Record this request
        INSERT INTO rate_limits (identifier, last_request_at)
        VALUES (p_identifier, v_current_time)
        ON DUPLICATE KEY UPDATE
            request_count = request_count + 1,
            last_request_at = v_current_time;
    END IF;
END//

DELIMITER ;

-- Indexes for performance optimization
CREATE INDEX idx_payments_date_range ON payments(created_at, status);
CREATE INDEX idx_webhook_processing ON webhook_log(processed, received_at);
CREATE INDEX idx_audit_search ON audit_log(event_type, created_at);

-- Initial data
INSERT INTO organizations (id, name, description, location, contact_phone, contact_email, website, logo_url, primary_color, secondary_color)
VALUES (
    'misjonarze-tarnow',
    'Misjonarze Parafia Świętej Rodziny',
    'Misjonarze świętego Wincentego a Paulo',
    'Tarnów',
    '790 525 400',
    'kontakt@misjonarze-tarnow.pl',
    'https://misjonarze-tarnow.pl',
    '/assets/mist_male_logo.png',
    '#4B6A9B',
    '#2C4770'
) ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

INSERT INTO goals (id, organization_id, name, description, icon, target_amount)
VALUES 
    ('church', 'misjonarze-tarnow', 'Ofiara na kościół', 'Wsparcie na utrzymanie i renowację kościoła parafialnego', 'church', 100000.00),
    ('poor', 'misjonarze-tarnow', 'Ofiara na ubogich', 'Pomoc potrzebującym w naszej wspólnocie parafialnej', 'heart', 50000.00),
    ('candles', 'misjonarze-tarnow', 'Ofiara za świeczki intencyjne', 'Intencje modlitewne za zmarłych i żyjących', 'candle', 30000.00)
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;