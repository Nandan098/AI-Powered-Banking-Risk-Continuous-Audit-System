CREATE OR REPLACE VIEW vw_open_audit_cases AS
SELECT *
FROM audit_cases
WHERE status = 'Open';

CREATE OR REPLACE VIEW vw_daily_risk AS
SELECT
    DATE(transaction_date) AS transaction_date,
    COUNT(*) AS transactions,
    SUM(amount) AS transaction_value,
    AVG(risk_score) AS avg_risk_score,
    COUNT(*) FILTER (WHERE risk_level='High') AS high_risk,
    COUNT(*) FILTER (WHERE risk_level='Medium') AS medium_risk
FROM (
    SELECT t.transaction_date, t.amount, r.risk_score, r.risk_level
    FROM transactions t
    JOIN risk_predictions r USING (transaction_id)
) x
GROUP BY DATE(transaction_date)
ORDER BY transaction_date;
