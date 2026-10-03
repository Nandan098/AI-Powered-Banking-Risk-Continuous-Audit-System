# Airflow Setup

The DAG is `dags/banking_risk_pipeline.py`.

It runs:
1. `scripts/run_pipeline.py`
2. `python -m src.db.load_postgres`

The example schedule is daily at 06:00. For local learning, first install Airflow in a Python 3.11 environment and configure the project volume as `/opt/project`, or adapt the BashOperator command to your environment.
