import pandas as pd
from src.risk.rules import apply_business_rules


def test_business_rules_create_score_and_reason():
    df = pd.DataFrame({
        "amount_robust_z":[7.0],
        "tx_count_10m":[6],
        "tx_count_1h":[6],
        "duplicate_candidate_2min":[1],
        "location_distance_km":[1000.0],
        "location_change":[1],
        "new_device":[1],
        "amount_to_customer_median":[6.0],
        "prior_customer_tx_count":[20],
        "channel_prior_share":[0.01],
    })
    out = apply_business_rules(df)
    assert out.loc[0,"rule_count"] >= 4
    assert out.loc[0,"rule_score"] > 0
    assert out.loc[0,"rule_reason"]
