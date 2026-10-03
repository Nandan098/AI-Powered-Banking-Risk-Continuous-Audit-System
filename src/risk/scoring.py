import numpy as np
import pandas as pd


def _norm(s: pd.Series, q_low=.01, q_high=.99):
    lo, hi = s.quantile(q_low), s.quantile(q_high)
    x = s.clip(lo, hi)
    if hi == lo:
        return pd.Series(0.5, index=s.index)
    return ((x-lo)/(hi-lo)).clip(0,1)


def build_risk_scores(df: pd.DataFrame, high_threshold: float, medium_threshold: float) -> pd.DataFrame:
    out = df.copy()

    amount_behavior = _norm(out["amount_robust_z"])
    velocity_behavior = _norm(out["tx_count_10m"] + out["tx_count_1h"]/10)
    out["behavior_score"] = (0.65*amount_behavior + 0.35*velocity_behavior).clip(0,1)

    distance_context = _norm(out["location_distance_km"])
    novelty_context = (out["new_device"]*0.5 + (1-out["channel_prior_share"].clip(0,1))*0.3 + out["location_change"]*0.2)
    out["context_score"] = (0.65*distance_context + 0.35*novelty_context).clip(0,1)

    # Model is intentionally the largest component; rules provide auditable reasons.
    out["risk_score"] = (
        0.55*out["ml_anomaly_score"]
        + 0.25*out["rule_score"]
        + 0.10*out["behavior_score"]
        + 0.10*out["context_score"]
    ).clip(0,1)

    out["risk_level"] = np.select(
        [out["risk_score"] >= high_threshold, out["risk_score"] >= medium_threshold],
        ["High","Medium"],
        default="Low"
    )
    out["risk_priority"] = out["risk_level"].map({"High":1,"Medium":2,"Low":3})
    out["risk_reason"] = np.where(
        out["rule_reason"].eq("model anomaly only"),
        "model anomaly score elevated",
        out["rule_reason"]
    )
    return out
