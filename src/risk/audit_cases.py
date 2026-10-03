import pandas as pd
import numpy as np


def build_audit_cases(risk_predictions: pd.DataFrame) -> pd.DataFrame:
    cases = risk_predictions[risk_predictions["risk_level"].isin(["High","Medium"])].copy()
    cases = cases.sort_values(["risk_priority","risk_score"], ascending=[True,False]).reset_index(drop=True)
    cases["case_id"] = [f"AC{i:07d}" for i in range(1,len(cases)+1)]
    cases["created_at"] = pd.Timestamp.utcnow().tz_localize(None)
    cases["status"] = "Open"
    cases["reviewed_by"] = ""
    cases["resolution"] = ""
    cases["priority"] = cases["risk_level"].map({"High":"High","Medium":"Medium"})

    cols = [
        "case_id","transaction_id","customer_id","account_id","transaction_date",
        "amount","risk_score","risk_level","priority","risk_reason","rule_count",
        "ml_anomaly_score","created_at","status","reviewed_by","resolution"
    ]
    return cases[cols]
