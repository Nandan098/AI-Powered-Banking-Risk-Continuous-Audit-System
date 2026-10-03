import numpy as np
import pandas as pd


def apply_business_rules(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Project-designed controls. These are not real bank policies.
    out["rule_large_relative"] = (out["amount_robust_z"] >= 6).astype(int)
    out["rule_velocity"] = ((out["tx_count_10m"] >= 5) | (out["tx_count_1h"] >= 15)).astype(int)
    out["rule_duplicate"] = (out["duplicate_candidate_2min"] == 1).astype(int)
    out["rule_location"] = ((out["location_distance_km"] >= 800) & (out["location_change"] == 1)).astype(int)
    out["rule_new_device"] = (
        (out["new_device"] == 1) & (out["amount_to_customer_median"] >= 5)
    ).astype(int)
    out["rule_rare_channel"] = (
        (out["prior_customer_tx_count"] >= 10) & (out["channel_prior_share"] < 0.02)
    ).astype(int)

    weights = {
        "rule_large_relative":0.30,
        "rule_velocity":0.25,
        "rule_duplicate":0.20,
        "rule_location":0.15,
        "rule_new_device":0.05,
        "rule_rare_channel":0.05,
    }
    out["rule_score"] = sum(out[col]*w for col,w in weights.items()).clip(0,1)

    labels = {
        "rule_large_relative":"amount unusual vs customer baseline",
        "rule_velocity":"high transaction velocity",
        "rule_duplicate":"near-duplicate transaction pattern",
        "rule_location":"unusual transaction location",
        "rule_new_device":"new device with unusual amount",
        "rule_rare_channel":"rare channel for customer",
    }

    def make_reason(row):
        reasons = [labels[col] for col in labels if row[col] == 1]
        return "; ".join(reasons) if reasons else "model anomaly only"

    out["rule_reason"] = out.apply(make_reason, axis=1)
    out["rule_count"] = out[list(weights)].sum(axis=1).astype(int)
    return out
