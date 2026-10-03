from pathlib import Path
import pandas as pd


def build_powerbi_tables(risk_df: pd.DataFrame, cases: pd.DataFrame, report_dir: Path):
    report_dir.mkdir(parents=True, exist_ok=True)

    overview = pd.DataFrame([{
        "total_transactions": len(risk_df),
        "total_transaction_value": risk_df["amount"].sum(),
        "high_risk_transactions": int((risk_df["risk_level"]=="High").sum()),
        "medium_risk_transactions": int((risk_df["risk_level"]=="Medium").sum()),
        "low_risk_transactions": int((risk_df["risk_level"]=="Low").sum()),
        "open_audit_cases": int((cases["status"]=="Open").sum()) if len(cases) else 0,
        "avg_risk_score": risk_df["risk_score"].mean(),
        "high_risk_value": risk_df.loc[risk_df["risk_level"]=="High","amount"].sum(),
    }])
    overview.to_csv(report_dir / "risk_overview.csv", index=False)

    temp = risk_df.copy()
    temp["date"] = pd.to_datetime(temp["transaction_date"]).dt.date
    daily = temp.groupby("date").agg(
        transactions=("transaction_id","count"),
        transaction_value=("amount","sum"),
        avg_risk_score=("risk_score","mean"),
        high_risk=("risk_level",lambda s:(s=="High").sum()),
        medium_risk=("risk_level",lambda s:(s=="Medium").sum()),
    ).reset_index()
    daily.to_csv(report_dir / "risk_by_day.csv", index=False)

    by_channel = temp.groupby("channel").agg(
        transactions=("transaction_id","count"),
        transaction_value=("amount","sum"),
        avg_risk_score=("risk_score","mean"),
        high_risk=("risk_level",lambda s:(s=="High").sum()),
        medium_risk=("risk_level",lambda s:(s=="Medium").sum()),
    ).reset_index().sort_values("transactions", ascending=False)
    by_channel.to_csv(report_dir / "risk_by_channel.csv", index=False)

    by_location = temp.groupby("location").agg(
        transactions=("transaction_id","count"),
        transaction_value=("amount","sum"),
        avg_risk_score=("risk_score","mean"),
        high_risk=("risk_level",lambda s:(s=="High").sum()),
    ).reset_index().sort_values("transactions", ascending=False)
    by_location.to_csv(report_dir / "risk_by_location.csv", index=False)

    # Explode audit reason strings for explainability.
    reason = (
        risk_df[["transaction_id","risk_level","risk_score","rule_reason"]]
        .assign(reason=lambda d:d["rule_reason"].str.split("; "))
        .explode("reason")
        .groupby("reason")
        .agg(
            flagged_transactions=("transaction_id","count"),
            avg_risk_score=("risk_score","mean"),
            high_risk=("risk_level",lambda s:(s=="High").sum()),
        ).reset_index().sort_values("flagged_transactions",ascending=False)
    )
    reason.to_csv(report_dir / "risk_by_reason.csv", index=False)

    risk_df.to_csv(report_dir / "transaction_risk.csv", index=False)
    cases.to_csv(report_dir / "audit_cases.csv", index=False)
