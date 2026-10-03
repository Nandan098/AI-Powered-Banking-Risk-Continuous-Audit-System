# Project Flow

```text
Synthetic Banking Data
        ↓
Raw Data EDA & Profiling
        ↓
Feature Engineering
        ↓
Behavioral Baselines
        ↓
Business Rules ─────────┐
        ↓               │
Isolation Forest ML ────┤
        ↓               │
      Risk Scoring <────┘
        ↓
Low / Medium / High
        ↓
Audit Case Queue
        ↓
PostgreSQL
        ↓
FastAPI
        ↓
Power BI
```

Airflow orchestrates the pipeline stages.
