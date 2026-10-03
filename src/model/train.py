from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import average_precision_score, precision_score, recall_score, f1_score

MODEL_FEATURES = [
    "log_amount", "amount_robust_z", "amount_to_customer_median",
    "tx_count_10m", "tx_count_1h", "tx_count_24h", "minutes_since_prev_tx",
    "location_distance_km", "location_change", "new_device",
    "duplicate_candidate_2min", "channel_prior_share",
    "merchant_category_prior_share", "is_weekend", "hour_sin", "hour_cos"
]


def _normalize_anomaly(raw_scores: np.ndarray) -> np.ndarray:
    # Higher = more anomalous. Robustly cap extreme score tails.
    lo, hi = np.quantile(raw_scores, [0.01, 0.99])
    clipped = np.clip(raw_scores, lo, hi)
    if hi == lo:
        return np.full_like(clipped, 0.5, dtype=float)
    return (clipped - lo) / (hi - lo)


def train_and_score(features: pd.DataFrame, train_end: str, model_dir: Path, contamination: float, random_state: int):
    model_dir.mkdir(parents=True, exist_ok=True)
    x = features[MODEL_FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    cutoff = pd.Timestamp(train_end)
    train_mask = features["transaction_date"] < cutoff

    scaler = RobustScaler()
    x_train = scaler.fit_transform(x.loc[train_mask])
    x_all = scaler.transform(x)

    model = IsolationForest(
        n_estimators=300,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(x_train)

    # decision_function: higher = more normal; invert it.
    raw = -model.decision_function(x_all)
    anomaly_score = _normalize_anomaly(raw)

    scored = features[["transaction_id"]].copy()
    scored["ml_raw_anomaly"] = raw
    scored["ml_anomaly_score"] = anomaly_score
    scored["model_training_rows"] = int(train_mask.sum())
    scored["model_train_end"] = cutoff

    joblib.dump(model, model_dir / "isolation_forest.joblib")
    joblib.dump(scaler, model_dir / "robust_scaler.joblib")
    (model_dir / "model_features.json").write_text(
        __import__("json").dumps(MODEL_FEATURES, indent=2), encoding="utf-8"
    )
    return scored


def evaluate(scored: pd.DataFrame, truth: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    merged = scored.merge(truth, on="transaction_id", how="left")
    y = merged["is_controlled_anomaly"].fillna(0).astype(int)
    score = merged["ml_anomaly_score"].astype(float)
    threshold = np.quantile(score, 0.985)
    pred = (score >= threshold).astype(int)

    metrics = pd.DataFrame([{
        "evaluation_type": "Isolation Forest top 1.5% anomaly score",
        "threshold": float(threshold),
        "average_precision": float(average_precision_score(y, score)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "flagged_records": int(pred.sum()),
        "controlled_anomalies": int(y.sum()),
    }])

    scenario = (
        merged.groupby("scenario")
        .agg(
            transactions=("transaction_id","count"),
            avg_ml_score=("ml_anomaly_score","mean"),
            p90_ml_score=("ml_anomaly_score",lambda s: s.quantile(.90)),
            top_1_5pct_flag_rate=("ml_anomaly_score",lambda s: float((s>=threshold).mean()))
        )
        .reset_index()
    )
    return metrics, scenario
