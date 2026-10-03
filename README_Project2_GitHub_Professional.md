# AI-Powered Banking Risk & Continuous Audit System

> **An end-to-end banking analytics and audit-support platform that combines behavioral anomaly detection, explainable business rules, risk scoring, audit-case generation, PostgreSQL, FastAPI, Power BI and Airflow.**

This project simulates a realistic banking transaction environment and demonstrates how transaction data can be transformed into **behavioral features, anomaly signals, risk-prioritized review cases and business-facing monitoring dashboards**.

The design is intentionally **risk-analysis-first, not a claim of fraud detection**. The system identifies transactions that are potentially unusual according to the project's model and controls, then prioritizes them for human review.

---

## 1. Project Overview

### Business problem

A bank processes a large number of transactions across multiple channels, customers, merchants, locations and devices.

Reviewing every transaction manually is inefficient. A technology-supported audit process can instead:

1. collect and validate transaction data;
2. understand normal customer behavior;
3. identify transactions that deviate from those patterns;
4. combine statistical/ML signals with explicit business rules;
5. assign a configurable risk score;
6. prioritize cases for review;
7. expose the results through APIs and dashboards.

This project demonstrates that complete workflow.

### Core objective

Build a system that answers:

> **Which transactions are potentially unusual, why were they flagged, how should they be prioritized for review, and how can the review workload be monitored continuously?**

---

# 2. End-to-End Architecture

```text
                         ┌─────────────────────┐
                         │    Raw Banking Data │
                         │ customers/accounts  │
                         │ merchants/devices   │
                         │ transactions        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       EDA           │
                         │ Profiling & Checks  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Cleaning & Typing   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Feature Engineering │
                         │ behavior / context  │
                         └──────────┬──────────┘
                                    │
                      ┌─────────────┴─────────────┐
                      │                           │
                      ▼                           ▼
            ┌──────────────────┐        ┌────────────────────┐
            │ Business Rules  │        │ Isolation Forest   │
            │ explainable     │        │ anomaly detection  │
            └────────┬─────────┘        └──────────┬─────────┘
                     │                             │
                     └──────────────┬──────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │    Risk Scoring     │
                         │  Low / Medium / High│
                         └──────────┬──────────┘
                                    ▼
                         ┌─────────────────────┐
                         │    Audit Cases      │
                         │ prioritized queue   │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
              ┌──────────────┐              ┌─────────────┐
              │ PostgreSQL   │              │   FastAPI   │
              │ persistence  │              │ API access │
              └──────┬───────┘              └──────┬──────┘
                     │                             │
                     └──────────────┬──────────────┘
                                    ▼
                            ┌──────────────┐
                            │   Power BI   │
                            │ Risk + Audit │
                            └──────────────┘

                 Airflow orchestrates the scheduled workflow.
```

### Simplified project flow

```text
Raw Transactions
      ↓
EDA
      ↓
Cleaning
      ↓
Feature Engineering
      ↓
Business Rules + Isolation Forest
      ↓
Risk Score
      ↓
Risk Level / Priority
      ↓
Audit Queue
      ↓
PostgreSQL / FastAPI
      ↓
Power BI
```

---

# 3. Dataset

## Dataset scale

| Dataset | Records |
|---|---:|
| Customers | 6,000 |
| Accounts | 9,451 |
| Merchants | 4,500 |
| Customer Devices | 7,637 |
| Transactions | 200,000 |

The dataset is intentionally not equally weighted.

It contains:

- long-tailed transaction amounts;
- long-tailed account balances;
- different customer activity levels;
- different numbers of accounts and devices;
- unequal channel volumes;
- unequal merchant-category frequencies;
- normal customer mobility plus a smaller number of unusual location changes;
- rare, unevenly distributed controlled evaluation scenarios.

---

# 4. Raw Data Model

```text
customers
    │
    ├────────────── accounts
    │                    │
    │                    └──────────── transactions
    │
    ├────────────── customer_devices
    │                    │
    │                    └──────────── transactions
    │
    └────────────────────┘

merchants
    │
    └──────────── transactions
```

## Raw files

```text
data/raw/
├── customers.csv
├── accounts.csv
├── merchants.csv
├── customer_devices.csv
└── transactions.csv
```

## Evaluation-only reference

```text
data/reference/
└── transaction_ground_truth.csv
```

The ground-truth file contains **project-created controlled scenarios for evaluation only**.

The following fields are **not used as model inputs**:

```text
scenario
is_controlled_anomaly
```

This is important because the project uses an unsupervised anomaly-detection approach.

---

# 5. Exploratory Data Analysis

The first stage is a systematic EDA and data-quality review.

Notebook:

```text
notebooks/01_eda_clean.ipynb
```

The EDA checks:

### Structure

- shape
- column count
- data types
- file size
- memory usage
- sample records

### Data quality

- missing values
- duplicate rows
- duplicate IDs
- invalid values
- primary-key consistency

### Distributions

- transaction amount
- customer income
- account balance
- transaction frequency
- channel usage
- merchant-category usage

### Relationships

- customer → account
- account → transaction
- customer → device
- merchant → transaction

### Chronology

A transaction should not occur before the corresponding account was opened.

---

# 6. Data Cleaning

The cleaning layer creates a processed version instead of overwriting the raw source files.

Cleaning includes:

- standardized column names;
- explicit date parsing;
- numeric type conversion;
- whitespace normalization;
- duplicate handling;
- domain validation;
- foreign-key validation;
- chronology validation.

The project follows an important banking-data principle:

> **An extreme value is not automatically an error.**

A high-value transaction may be perfectly legitimate. Therefore, extreme observations are investigated as potential anomalies rather than automatically deleted.

---

# 7. Feature Engineering

The core behavioral feature pipeline is implemented in:

```text
src/features/build_features.py
```

The model does not rely only on a fixed transaction amount threshold.

Instead, features describe how a transaction compares with **the customer's observed behavior and transaction context**.

## Amount behavior

Examples:

```text
log_amount
customer_median_amount
customer_IQR
robust_amount_deviation
amount_to_customer_baseline
```

## Velocity behavior

Examples:

```text
transactions_last_10_min
transactions_last_1_hour
transactions_last_24_hours
previous_transaction_gap
```

## Context / novelty

Examples:

```text
location_distance
location_change
new_device_flag
channel_rarity
merchant_category_rarity
```

## Time features

Examples:

```text
transaction_hour
day_of_week
weekend_flag
cyclical_hour_encoding
```

These features create a more contextual anomaly-detection problem than simply asking whether an amount exceeds a fixed threshold.

---

# 8. Business Rule Engine

Business rules are implemented separately so that the system remains explainable.

File:

```text
src/risk/rules.py
```

The project includes controls such as:

### Large relative transaction

A transaction that is unusually large compared with the customer's historical baseline.

### Velocity

Unusually high transaction frequency inside a short rolling window.

### Duplicate-like transaction

Near-duplicate transaction attributes occurring within a short time interval on the same account.

### Location anomaly

A large geographic deviation from the customer's usual/home location.

### New device

A first-seen device combined with unusual transaction behavior.

### Rare channel

A transaction channel that is historically uncommon for the customer.

> These are **project-designed controls for demonstration**. They are not IndusInd Bank's internal rules or policies.

---

# 9. Machine Learning

## Model

**Isolation Forest**

with:

```text
RobustScaler
        ↓
Isolation Forest
```

Model artifacts:

```text
models/isolation_forest.joblib
models/robust_scaler.joblib
models/model_features.json
```

## Why Isolation Forest?

The problem is framed as:

> **Find observations that are unusual relative to the broader transaction population.**

This fits an unsupervised anomaly-detection workflow because the model does not require the synthetic evaluation labels as training targets.

## Training design

The model is trained on an earlier period defined by the project configuration and then used to score the broader transaction period.

This gives the project a simple chronological development setup rather than randomly mixing every timestamp into training.

---

# 10. Features Excluded From Risk Scoring

The model intentionally excludes demographic variables such as:

```text
gender
occupation
```

Annual income is also excluded from risk scoring.

The model therefore focuses on:

```text
observed transaction behavior
+
transaction context
+
customer activity patterns
```

This helps keep the demonstrated risk signal centered on transaction behavior rather than socioeconomic attributes.

---

# 11. Risk Scoring

The ML model produces an anomaly signal.

The rule engine produces explicit business-control evidence.

These signals are then combined into a configurable risk score.

```text
                  ML anomaly signal
                         +
                business-rule evidence
                         +
               behavioral/context data
                         ↓
                   Risk Score
                         ↓
              ┌──────────┼──────────┐
              ▼          ▼          ▼
             Low       Medium      High
```

The exact weights and thresholds are project configuration rather than bank policy.

Source:

```text
src/risk/scoring.py
```

---

# 12. Audit Case Generation

High-priority transactions are converted into audit cases.

Source:

```text
src/risk/audit_cases.py
```

An audit case can contain:

```text
case_id
transaction_id
customer_id
amount
risk_score
risk_level
priority
risk_reason
rule_count
ml_anomaly_score
created_at
status
reviewed_by
resolution
```

Example:

```text
Case ID: AC000184
Transaction: T00192834
Risk Score: 0.86
Risk Level: HIGH
Priority: High

Reasons:
- unusual transaction amount
- unusual location
- unusual transaction frequency

Status:
Open
```

The important workflow is:

```text
Potentially unusual transaction
             ↓
        Risk priority
             ↓
         Audit case
             ↓
     Human investigation
             ↓
        Resolution
```

The system does **not** treat a risk score as proof of fraud or misconduct.

---

# 13. PostgreSQL

The project provides a relational database layer.

```text
sql/
├── schema.sql
├── views.sql
└── analytics_queries.sql
```

The database is intended to persist:

```text
customers
accounts
merchants
customer_devices
transactions
transaction_features
risk_predictions
audit_cases
```

This creates a clear separation between:

```text
operational/raw data
        ↓
processed features
        ↓
risk outputs
        ↓
audit workflow
```

---

# 14. FastAPI

The API layer provides programmatic access to risk and audit outputs.

Source:

```text
src/api/main.py
```

The project exposes audit-oriented endpoints for retrieving and reviewing cases.

Example workflow:

```text
GET  /transactions
GET  /risk-alerts
GET  /audit-cases
GET  /audit-cases/{id}
POST /audit-cases/{id}/review
```

# 15. Power BI Dashboard

The report uses the curated files under:

```text
data/powerbi/
```

## Page 1 — Risk Overview

Purpose:

> **What is the overall risk picture?**

Recommended elements:

```text
Total Transactions
High Risk
Medium Risk
Low Risk
Open Audit Cases
Transaction Value
```

Visuals:

```text
Risk distribution
Daily risk trend
Risk by channel
Risk by location
Risk reasons
```

---

## Page 2 — Transaction Risk Analysis

Purpose:

> **Why was a transaction flagged?**

Main source:

```text
data/powerbi/transaction_risk.csv
```

Visuals:

```text
Transaction amount vs risk score
Risk-score distribution
ML score vs rule score
Risk by merchant category
High-risk transaction detail table
```

Suggested transaction-level columns:

```text
transaction_id
customer_id
transaction_date
amount
channel
merchant_category
location
ml_anomaly_score
rule_score
risk_score
risk_level
risk_reason
```

Useful slicers:

```text
risk_level
channel
merchant_category
location
status
date
```

---

## Page 3 — Continuous Audit Monitor

Purpose:

> **How are potentially unusual transactions being prioritized and reviewed?**

Main sources:

```text
audit_cases.csv
risk_by_reason.csv
risk_by_channel.csv
combined_risk_evaluation.csv
scenario_detection.csv
```

Visuals:

```text
Open cases by priority
Audit cases by reason
Cases by channel
Case status/resolution table
Model evaluation metrics
Scenario detection summary
```

---

# 16. Power BI Data Sources

The dashboard-ready files are:

```text
data/powerbi/
├── risk_overview.csv
├── transaction_risk.csv
├── audit_cases.csv
├── risk_by_day.csv
├── risk_by_channel.csv
├── risk_by_location.csv
├── risk_by_reason.csv
├── model_evaluation.csv
├── combined_risk_evaluation.csv
└── scenario_detection.csv
```

See:

```text
docs/POWER_BI_BUILD_GUIDE.md
```

for the visual-by-visual build instructions.

---

# 17. Airflow

The Airflow DAG is:

```text
dags/banking_risk_pipeline.py
```

Conceptual flow:

```text
Extract
  ↓
Clean
  ↓
Feature Engineering
  ↓
Business Rules
  ↓
Model Scoring
  ↓
Risk Scoring
  ↓
Audit Case Generation
  ↓
Reporting Outputs
```

Airflow is the orchestration layer used to schedule and manage this workflow.

Setup instructions:

```text
docs/AIRFLOW_SETUP.md
```

---

# 18. Testing

The project includes automated tests for:

```text
tests/
├── test_features.py
├── test_integrity.py
├── test_rules.py
└── test_scoring.py
```

Run:

```bash
pytest
```

The tests cover areas such as:

- feature-generation behavior
- relational integrity
- rule outputs
- risk-score behavior

---

# 19. Project Results

The included synthetic development run produced:

| Metric | Result |
|---|---:|
| Transactions scored | 200,000 |
| High risk | 247 |
| Medium risk | 2,961 |
| Low risk | 196,792 |
| Audit cases | 3,208 |

### Isolation Forest evaluation

| Metric | Result |
|---|---:|
| Average Precision | 0.0673 |
| Precision at top-1.5% cutoff | 0.0623 |
| Recall | 0.0656 |
| F1 | 0.0639 |

### Combined risk-score evaluation

| Metric | Result |
|---|---:|
| Average Precision | 0.0703 |
| Precision at configured high-risk threshold | 0.1093 |
| Recall | 0.0095 |
| F1 | 0.0174 |

These are **development metrics on synthetic controlled scenarios**.

They are not production performance claims.

Detailed results:

```text
docs/RESULTS.md
```

---

# 20. Interpretation of Model Results

The evaluation is intentionally included as part of the project.

A real ML project should not only say:

> "The model works."

It should also measure:

- precision
- recall
- F1
- ranking quality
- threshold behavior
- performance on different scenario types

The relatively low development metrics show why an anomaly score should be treated as a **review-prioritization signal**, not as a final decision.

A production system would need:

```text
better labeled data
+
threshold calibration
+
model validation
+
false-positive analysis
+
model monitoring
+
human review
+
governance
```

---

# 21. Important Risk-Modeling Principles

## Risk score ≠ fraud

A transaction being assigned a high risk score does not establish that it is fraudulent.

The project language should therefore use:

```text
potentially unusual transaction
higher-risk transaction
transaction requiring review
```

rather than:

```text
confirmed fraud
fraudulent customer
criminal transaction
```

## Rules are explainable

The rules provide textual reasons for why a transaction was flagged.

Example:

```text
unusual amount
+
unusual location
+
velocity anomaly
```

This is more interpretable than presenting only an ML probability.

## Human review remains important

The intended workflow is:

```text
ML / rules
    ↓
prioritization
    ↓
audit review
    ↓
human resolution
```

---

# 22. Project Structure

```text
Project2_AI_Banking_Risk_Continuous_Audit/
│
├── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── accounts.csv
│   │   ├── merchants.csv
│   │   ├── customer_devices.csv
│   │   └── transactions.csv
│   │
│   ├── reference/
│   │   └── transaction_ground_truth.csv
│   │
│   ├── processed/
│   ├── powerbi/
│   └── reports/
│
├── notebooks/
│   ├── 01_eda_clean.ipynb
│   └── 02_feature_engineering_modeling.ipynb
│
├── src/
│   ├── cleaning/
│   ├── eda/
│   ├── features/
│   ├── model/
│   ├── risk/
│   ├── reporting/
│   ├── db/
│   └── api/
│
├── sql/
│   ├── schema.sql
│   ├── views.sql
│   └── analytics_queries.sql
│
├── dags/
│   └── banking_risk_pipeline.py
│
├── tests/
│   ├── test_features.py
│   ├── test_integrity.py
│   ├── test_rules.py
│   └── test_scoring.py
│
├── models/
│   ├── isolation_forest.joblib
│   ├── robust_scaler.joblib
│   └── model_features.json
│
├── dashboard/
│   ├── README.md
│   └── theme.json
│
├── docs/
│   ├── RESULTS.md
│   ├── AIRFLOW_SETUP.md
│   ├── POWER_BI_BUILD_GUIDE.md
│   ├── MODEL_CARD.md
│   ├── INTERVIEW_STORY.md
│   ├── ASSUMPTIONS_AND_LIMITATIONS.md
│   ├── RISK_RULES.md
│   ├── DATA_DICTIONARY.md
│   ├── PROJECT_FLOW.md
│   ├── TECHNICAL_DESIGN.md
│   └── RESUME_BULLETS.md
│
├── scripts/
│   ├── run_pipeline.py
│   ├── eda.py
│   └── run_api.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-airflow.txt
├── .env.example
├── run_project.bat
├── run_project.sh
└── README.md
```

---

# 23. Tech Stack

| Layer | Technology |
|---|---|
| Programming | Python |
| Data Processing | Pandas, NumPy |
| ML | Scikit-learn |
| Anomaly Detection | Isolation Forest |
| Database | PostgreSQL |
| API | FastAPI |
| Dashboard | Power BI |
| Orchestration | Apache Airflow |
| Testing | Pytest |
| Containers | Docker |
| Version Control | Git / GitHub |

---
