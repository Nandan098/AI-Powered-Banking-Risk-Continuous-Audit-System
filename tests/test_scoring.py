import pandas as pd
from src.risk.scoring import build_risk_scores


def test_risk_score_bounds_and_levels():
    df = pd.DataFrame({
        "ml_anomaly_score":[0.1,0.8,0.95],
        "rule_score":[0.0,0.6,1.0],
        "amount_robust_z":[0.1,5.0,10.0],
        "tx_count_10m":[0,4,10],
        "tx_count_1h":[1,10,20],
        "location_distance_km":[0,500,2000],
        "new_device":[0,1,1],
        "channel_prior_share":[0.5,0.01,0.005],
        "location_change":[0,1,1],
        "rule_reason":["model anomaly only","x","y"],
    })
    out = build_risk_scores(df, 0.75, 0.45)
    assert out["risk_score"].between(0,1).all()
    assert set(out["risk_level"]).issubset({"Low","Medium","High"})
