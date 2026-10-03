# AI-Powered Banking Risk & Continuous Audit System

A complete portfolio project that combines behavioral anomaly detection, explainable business rules, risk scoring,
audit-case generation, PostgreSQL, FastAPI, Power BI and Airflow.

## Dataset

The included dataset is synthetic but designed to have non-uniform banking behavior.
- Customers: 6,000
- Accounts: 9,451
- Merchants: 4,500
- Customer devices: 7,637
- Transactions: 200,000

The data intentionally has long-tailed transaction amounts and balances, unequal transaction volumes by channel,
heterogeneous customer activity, different numbers of accounts/devices, and unequal anomaly scenarios.

## Project architecture

```text
Raw Data → EDA → Cleaning → Feature Engineering → Business Rules + Isolation Forest
        → Risk Scoring → Audit Cases → PostgreSQL → FastAPI → Power BI
```

Airflow orchestrates the pipeline in scheduled runs.

## ML design

Isolation Forest is trained without using the evaluation-only ground-truth labels.
The model focuses on transaction behavior and context. Demographic fields such as gender and occupation are excluded
from risk scoring, and annual income is excluded from the model features.

## Run locally

### 1. Create environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the complete analytical pipeline

```bash
python scripts/run_pipeline.py
```

This creates:
- `data/processed/customers.csv` and other cleaned base tables
- `data/processed/transaction_features.csv`
- `data/processed/risk_predictions.csv`
- `data/processed/audit_cases.csv`
- `data/powerbi/*.csv`
- `data/reports/*.csv/json`
- `models/*.joblib`

### 4. Run tests

```bash
pytest
```

### 5. Start PostgreSQL with Docker

```bash
docker compose up -d postgres
```

Then load the processed outputs:

```bash
python -m src.db.load_postgres
```

### 6. Start API

```bash
uvicorn src.api.main:app --reload
```

Open:
`http://localhost:8000/docs`

### 7. Power BI

Import the CSVs from `data/powerbi/`.

Main files:
- `risk_overview.csv`
- `risk_by_day.csv`
- `risk_by_channel.csv`
- `risk_by_location.csv`
- `risk_by_reason.csv`
- `transaction_risk.csv`
- `audit_cases.csv`
- `model_evaluation.csv`
- `scenario_detection.csv`

See `docs/POWER_BI_BUILD_GUIDE.md`.

## Evaluation

The file `data/reference/transaction_ground_truth.csv` contains controlled, project-created anomaly scenarios.
It exists to evaluate the unsupervised detector; it is not a model feature and does not represent real bank fraud labels.

## Important limitation

This is a synthetic portfolio project. It is not a production fraud-detection system and risk scores do not establish
fraud, wrongdoing, or customer intent. Real deployment would require model governance, validation on real data,
threshold calibration, monitoring, human review, security and regulatory controls.
