import argparse
import pandas as pd
from sqlalchemy import create_engine, text
from src.config import DATABASE_URL, PROCESSED_DIR, PROJECT_ROOT

BASE_TABLES = {
    "customers":"customers.csv",
    "accounts":"accounts.csv",
    "merchants":"merchants.csv",
    "customer_devices":"customer_devices.csv",
    "transactions":"transactions.csv",
}


def _execute_file(conn, path):
    sql = path.read_text(encoding="utf-8")
    for statement in [s.strip() for s in sql.split(";") if s.strip()]:
        conn.execute(text(statement))


def load_postgres(database_url=DATABASE_URL):
    engine = create_engine(database_url)
    with engine.begin() as conn:
        # Rebuild analytical tables cleanly for repeatable local runs.
        conn.execute(text("DROP VIEW IF EXISTS vw_daily_risk CASCADE"))
        conn.execute(text("DROP VIEW IF EXISTS vw_open_audit_cases CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS audit_cases CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS risk_predictions CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS transaction_features CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS transactions CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS customer_devices CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS merchants CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS accounts CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS customers CASCADE"))
        _execute_file(conn, PROJECT_ROOT / "sql" / "schema.sql")

    # Load base tables in FK-safe order using append into typed schema tables.
    for table, fname in BASE_TABLES.items():
        df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / fname)
        df.to_sql(table, engine, if_exists="append", index=False, chunksize=5000, method="multi")

    features = pd.read_csv(PROCESSED_DIR / "transaction_features.csv")
    risk = pd.read_csv(PROCESSED_DIR / "risk_predictions.csv")
    cases = pd.read_csv(PROCESSED_DIR / "audit_cases.csv")

    feature_cols = [
        "transaction_id","customer_median_amount","customer_iqr_amount","amount_robust_z",
        "amount_to_customer_median","prior_customer_tx_count","channel_prior_share",
        "merchant_category_prior_share","minutes_since_prev_tx","tx_count_10m","tx_count_1h",
        "tx_count_24h","location_distance_km","location_change","new_device",
        "duplicate_candidate_2min","hour","day_of_week","is_weekend","ml_anomaly_score",
        "rule_score","behavior_score","context_score","risk_score","risk_level","risk_reason"
    ]
    features[feature_cols].to_sql("transaction_features", engine, if_exists="append", index=False, chunksize=5000, method="multi")

    risk_cols=["transaction_id","ml_raw_anomaly","ml_anomaly_score","rule_score","behavior_score","context_score","risk_score","risk_level","risk_reason"]
    risk[risk_cols].to_sql("risk_predictions", engine, if_exists="append", index=False, chunksize=5000, method="multi")
    cases.to_sql("audit_cases", engine, if_exists="append", index=False, chunksize=5000, method="multi")

    with engine.begin() as conn:
        _execute_file(conn, PROJECT_ROOT / "sql" / "views.sql")

    print("PostgreSQL load complete")


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--database-url", default=DATABASE_URL)
    args=parser.parse_args()
    load_postgres(args.database_url)
