from pathlib import Path
import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

from src.config import DATABASE_URL

app = FastAPI(
    title="Banking Risk & Continuous Audit API",
    version="1.0.0",
    description="Read-only API for risk predictions and audit cases."
)

engine = create_engine(os.getenv("DATABASE_URL", DATABASE_URL), pool_pre_ping=True)


class AuditReview(BaseModel):
    status: str = Field(pattern="^(Open|In Review|Closed)$")
    reviewed_by: str = Field(default="", max_length=120)
    resolution: str = Field(default="", max_length=1000)


def fetch_all(sql, params=None):
    with engine.begin() as conn:
        return [dict(row._mapping) for row in conn.execute(text(sql), params or {})]


@app.get("/health")
def health():
    try:
        with engine.begin() as conn:
            conn.execute(text("SELECT 1"))
        return {"status":"ok"}
    except Exception as exc:
        return {"status":"degraded", "error":str(exc)}


@app.get("/risk-alerts")
def risk_alerts(
    level: str | None = Query(default=None, pattern="^(Low|Medium|High)$"),
    limit: int = Query(default=100, ge=1, le=1000)
):
    where = ""
    params = {"limit":limit}
    if level:
        where = "WHERE r.risk_level = :level"
        params["level"] = level
    return fetch_all(f"""
        SELECT r.transaction_id, t.customer_id, t.account_id, t.transaction_date,
               t.amount, t.channel, t.location,
               r.ml_anomaly_score, r.rule_score, r.risk_score,
               r.risk_level, r.risk_reason
        FROM risk_predictions r
        JOIN transactions t USING (transaction_id)
        {where}
        ORDER BY r.risk_score DESC
        LIMIT :limit
    """, params)


@app.get("/audit-cases")
def audit_cases(status: str | None = Query(default="Open"), limit: int = Query(default=100,ge=1,le=1000)):
    where = ""
    params = {"limit":limit}
    if status:
        where = "WHERE status = :status"
        params["status"] = status
    return fetch_all(f"""
        SELECT * FROM audit_cases
        {where}
        ORDER BY risk_score DESC
        LIMIT :limit
    """, params)


@app.get("/audit-cases/{case_id}")
def audit_case(case_id: str):
    rows = fetch_all("SELECT * FROM audit_cases WHERE case_id=:case_id", {"case_id":case_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Audit case not found")
    return rows[0]


@app.post("/audit-cases/{case_id}/review")
def review_audit_case(case_id: str, review: AuditReview):
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE audit_cases
                SET status=:status, reviewed_by=:reviewed_by, resolution=:resolution
                WHERE case_id=:case_id
            """),
            {
                "case_id": case_id,
                "status": review.status,
                "reviewed_by": review.reviewed_by,
                "resolution": review.resolution,
            }
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Audit case not found")

    return {"case_id":case_id, "status":review.status, "reviewed_by":review.reviewed_by}
