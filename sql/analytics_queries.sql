-- 1. Highest-risk transactions
SELECT transaction_id, customer_id, amount, risk_score, risk_level, risk_reason
FROM risk_predictions
JOIN transactions USING (transaction_id)
WHERE risk_level IN ('High','Medium')
ORDER BY risk_score DESC
LIMIT 100;

-- 2. Risk by channel
SELECT channel, COUNT(*) AS transactions,
       AVG(risk_score) AS avg_risk_score,
       COUNT(*) FILTER (WHERE risk_level='High') AS high_risk
FROM transactions
JOIN risk_predictions USING (transaction_id)
GROUP BY channel
ORDER BY transactions DESC;

-- 3. Risk exposure by location
SELECT location, COUNT(*) AS transactions,
       SUM(amount) AS transaction_value,
       COUNT(*) FILTER (WHERE risk_level='High') AS high_risk
FROM transactions
JOIN risk_predictions USING (transaction_id)
GROUP BY location
ORDER BY high_risk DESC, transaction_value DESC;

-- 4. Open audit workload
SELECT priority, COUNT(*) AS open_cases
FROM audit_cases
WHERE status='Open'
GROUP BY priority
ORDER BY priority;

-- 5. Customer risk concentration
SELECT customer_id,
       COUNT(*) AS flagged_transactions,
       SUM(amount) AS flagged_value,
       MAX(risk_score) AS max_risk_score
FROM transactions
JOIN risk_predictions USING (transaction_id)
WHERE risk_level IN ('High','Medium')
GROUP BY customer_id
ORDER BY flagged_value DESC;

-- 6. Failed/reversed transactions among flagged records
SELECT status, COUNT(*) AS flagged_transactions
FROM transactions
JOIN risk_predictions USING (transaction_id)
WHERE risk_level IN ('High','Medium')
GROUP BY status
ORDER BY flagged_transactions DESC;
