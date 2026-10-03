CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name TEXT,
    age INTEGER,
    gender TEXT,
    city TEXT,
    occupation TEXT,
    annual_income NUMERIC(16,2),
    customer_since DATE
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL REFERENCES customers(customer_id),
    account_type TEXT,
    opening_date DATE,
    balance NUMERIC(18,2),
    status TEXT
);

CREATE TABLE IF NOT EXISTS merchants (
    merchant_id VARCHAR(20) PRIMARY KEY,
    merchant_category TEXT,
    city TEXT,
    merchant_risk_band TEXT,
    merchant_size TEXT
);

CREATE TABLE IF NOT EXISTS customer_devices (
    device_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL REFERENCES customers(customer_id),
    device_type TEXT,
    first_seen DATE,
    last_seen DATE
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    account_id VARCHAR(20) NOT NULL REFERENCES accounts(account_id),
    customer_id VARCHAR(20) NOT NULL REFERENCES customers(customer_id),
    transaction_date TIMESTAMP,
    transaction_type TEXT,
    channel TEXT,
    amount NUMERIC(18,2),
    merchant_id VARCHAR(20) REFERENCES merchants(merchant_id),
    merchant_category TEXT,
    location TEXT,
    device_id VARCHAR(20) REFERENCES customer_devices(device_id),
    status TEXT
);

CREATE TABLE IF NOT EXISTS transaction_features (
    transaction_id VARCHAR(20) PRIMARY KEY REFERENCES transactions(transaction_id),
    customer_median_amount NUMERIC(18,2),
    customer_iqr_amount NUMERIC(18,2),
    amount_robust_z DOUBLE PRECISION,
    amount_to_customer_median DOUBLE PRECISION,
    prior_customer_tx_count INTEGER,
    channel_prior_share DOUBLE PRECISION,
    merchant_category_prior_share DOUBLE PRECISION,
    minutes_since_prev_tx DOUBLE PRECISION,
    tx_count_10m INTEGER,
    tx_count_1h INTEGER,
    tx_count_24h INTEGER,
    location_distance_km DOUBLE PRECISION,
    location_change INTEGER,
    new_device INTEGER,
    duplicate_candidate_2min INTEGER,
    hour INTEGER,
    day_of_week INTEGER,
    is_weekend INTEGER,
    ml_anomaly_score DOUBLE PRECISION,
    rule_score DOUBLE PRECISION,
    behavior_score DOUBLE PRECISION,
    context_score DOUBLE PRECISION,
    risk_score DOUBLE PRECISION,
    risk_level TEXT,
    risk_reason TEXT
);

CREATE TABLE IF NOT EXISTS risk_predictions (
    transaction_id VARCHAR(20) PRIMARY KEY REFERENCES transactions(transaction_id),
    ml_raw_anomaly DOUBLE PRECISION,
    ml_anomaly_score DOUBLE PRECISION,
    rule_score DOUBLE PRECISION,
    behavior_score DOUBLE PRECISION,
    context_score DOUBLE PRECISION,
    risk_score DOUBLE PRECISION,
    risk_level TEXT,
    risk_reason TEXT
);

CREATE TABLE IF NOT EXISTS audit_cases (
    case_id VARCHAR(20) PRIMARY KEY,
    transaction_id VARCHAR(20) NOT NULL REFERENCES transactions(transaction_id),
    customer_id VARCHAR(20),
    account_id VARCHAR(20),
    transaction_date TIMESTAMP,
    amount NUMERIC(18,2),
    risk_score DOUBLE PRECISION,
    risk_level TEXT,
    priority TEXT,
    risk_reason TEXT,
    rule_count INTEGER,
    ml_anomaly_score DOUBLE PRECISION,
    created_at TIMESTAMP,
    status TEXT,
    reviewed_by TEXT,
    resolution TEXT
);

CREATE INDEX IF NOT EXISTS idx_transactions_customer_date ON transactions(customer_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_risk_predictions_level ON risk_predictions(risk_level);
CREATE INDEX IF NOT EXISTS idx_audit_cases_status ON audit_cases(status);
