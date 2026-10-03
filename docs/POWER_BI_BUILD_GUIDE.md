# Power BI Build Guide — Project 2

Use the files in `data/powerbi/`.

## Page 1 — Risk Overview

Use:
- `risk_overview.csv` for KPI cards.
- `risk_by_day.csv` for risk trend.
- `risk_by_channel.csv` for channel analysis.
- `risk_by_location.csv` for location analysis.
- `risk_by_reason.csv` for explanation counts.

Recommended visuals:
1. KPI cards — total transactions, high risk, medium risk, open audit cases, transaction value.
2. Line chart — daily transactions / average risk score.
3. Column chart — high/medium risk by channel.
4. Bar chart — high-risk transaction value by location.
5. Bar chart — flagged transactions by reason.

## Page 2 — Transaction Risk Analysis

Use `transaction_risk.csv`.

Recommended visuals:
- Scatter: transaction amount vs risk score, size = amount, legend = risk level.
- Histogram/bar: risk score distribution.
- Table: transaction_id, customer_id, amount, channel, ml_anomaly_score, rule_score, risk_score, risk_level, risk_reason.
- Slicers: risk level, channel, merchant category, status, date.

## Page 3 — Continuous Audit Monitor

Use:
- `audit_cases.csv`
- `risk_by_reason.csv`
- `risk_by_channel.csv`
- `combined_risk_evaluation.csv`
- `scenario_detection.csv`

Recommended visuals:
- Open audit cases by priority.
- Audit cases by reason.
- Cases by channel.
- Case table with status/resolution.
- Model evaluation cards (precision, recall, F1) shown as development/evaluation metrics, not production guarantees.
