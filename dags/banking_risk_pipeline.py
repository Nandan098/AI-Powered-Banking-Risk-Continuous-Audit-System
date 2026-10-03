from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="banking_risk_continuous_audit_pipeline",
    start_date=datetime(2025,1,1),
    schedule="0 6 * * *",
    catchup=False,
    tags=["banking","risk","audit","ml"],
) as dag:
    run_pipeline = BashOperator(
        task_id="run_banking_risk_pipeline",
        bash_command="cd /opt/project && python scripts/run_pipeline.py",
    )

    load_postgres = BashOperator(
        task_id="load_postgres",
        bash_command="cd /opt/project && python -m src.db.load_postgres",
    )

    run_pipeline >> load_postgres
