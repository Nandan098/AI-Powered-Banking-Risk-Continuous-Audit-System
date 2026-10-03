from pathlib import Path
import json
import pandas as pd

from .config import (
    RAW_DIR, REFERENCE_DIR, PROCESSED_DIR, POWERBI_DIR, REPORT_DIR, MODEL_DIR,
    RANDOM_STATE, MODEL_CONTAMINATION, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD, TRAIN_END
)
from .io_utils import read_raw_tables
from .eda.profile import run_eda
from .cleaning.clean import clean_tables, validate_cleaned_tables
from .features.build_features import build_transaction_features
from .model.train import train_and_score, evaluate
from .risk.rules import apply_business_rules
from .risk.scoring import build_risk_scores
from .risk.audit_cases import build_audit_cases
from .reporting.powerbi import build_powerbi_tables


def run_pipeline():
    tables = read_raw_tables(RAW_DIR)

    # Stage 1: raw EDA/profiling reports.
    run_eda(tables, RAW_DIR, REPORT_DIR / "eda")

    # Stage 2: transaction feature store.
    features = build_transaction_features(
        tables["customers"],
        tables["accounts"],
        tables["merchants"],
        tables["customer_devices"],
        tables["transactions"],
    )
    features.to_csv(PROCESSED_DIR / "transaction_features.csv", index=False)

    # Stage 4: unsupervised anomaly model.
    ml_scores = train_and_score(
        features,
        train_end=TRAIN_END,
        model_dir=MODEL_DIR,
        contamination=MODEL_CONTAMINATION,
        random_state=RANDOM_STATE,
    )
    scores = features.merge(ml_scores, on="transaction_id", how="left")

    # Stage 5: explainable business rules.
    rules = apply_business_rules(scores)

    # Stage 6: combined risk scoring.
    risk = build_risk_scores(
        rules,
        high_threshold=HIGH_RISK_THRESHOLD,
        medium_threshold=MEDIUM_RISK_THRESHOLD,
    )
    risk.to_csv(PROCESSED_DIR / "risk_predictions.csv", index=False)

    # Stage 7: audit queue.
    cases = build_audit_cases(risk)
    cases.to_csv(PROCESSED_DIR / "audit_cases.csv", index=False)

    # Stage 8: evaluation using project-created labels only for evaluation.
    truth = pd.read_csv(REFERENCE_DIR / "transaction_ground_truth.csv")
    metrics, scenario = evaluate(ml_scores, truth)
    metrics.to_csv(REPORT_DIR / "model_evaluation.csv", index=False)
    scenario.to_csv(REPORT_DIR / "scenario_detection.csv", index=False)

    # Risk evaluation against controlled labels; not used as model input.
    eval_df = risk[["transaction_id","risk_score","risk_level"]].merge(truth,on="transaction_id",how="left")
    risk_threshold = HIGH_RISK_THRESHOLD
    eval_df["predicted_high_risk"] = (eval_df["risk_score"] >= risk_threshold).astype(int)
    from sklearn.metrics import precision_score, recall_score, f1_score, average_precision_score
    risk_metrics = pd.DataFrame([{
        "metric":"Combined risk score",
        "threshold":risk_threshold,
        "average_precision":float(average_precision_score(eval_df["is_controlled_anomaly"],eval_df["risk_score"])),
        "precision":float(precision_score(eval_df["is_controlled_anomaly"],eval_df["predicted_high_risk"],zero_division=0)),
        "recall":float(recall_score(eval_df["is_controlled_anomaly"],eval_df["predicted_high_risk"],zero_division=0)),
        "f1":float(f1_score(eval_df["is_controlled_anomaly"],eval_df["predicted_high_risk"],zero_division=0)),
    }])
    risk_metrics.to_csv(REPORT_DIR / "combined_risk_evaluation.csv", index=False)

    # Stage 9: Power BI-ready reporting layer.
    build_powerbi_tables(risk, cases, POWERBI_DIR)
    # Add model evaluation tables to Power BI layer.
    metrics.to_csv(POWERBI_DIR / "model_evaluation.csv", index=False)
    scenario.to_csv(POWERBI_DIR / "scenario_detection.csv", index=False)
    risk_metrics.to_csv(POWERBI_DIR / "combined_risk_evaluation.csv", index=False)

    summary = {
        "raw_tables": {k:int(len(v)) for k,v in tables.items()},
        "feature_rows": int(len(features)),
        "high_risk": int((risk["risk_level"]=="High").sum()),
        "medium_risk": int((risk["risk_level"]=="Medium").sum()),
        "low_risk": int((risk["risk_level"]=="Low").sum()),
        "audit_cases": int(len(cases)),
        "model_contamination": MODEL_CONTAMINATION,
        "train_end": TRAIN_END,
        "high_risk_threshold": HIGH_RISK_THRESHOLD,
        "medium_risk_threshold": MEDIUM_RISK_THRESHOLD,
    }
    (REPORT_DIR / "pipeline_summary.json").write_text(json.dumps(summary,indent=2,default=str),encoding="utf-8")
    return summary
