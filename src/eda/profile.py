from pathlib import Path
import pandas as pd
import numpy as np


def build_inventory(tables: dict, raw_dir: Path) -> pd.DataFrame:
    rows = []
    for name, df in tables.items():
        rows.append({
            "table": name,
            "rows": len(df),
            "columns": df.shape[1],
            "file_size_mb": round((raw_dir / f"{name}.csv").stat().st_size / 1024**2, 3),
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 3),
            "missing_cells": int(df.isna().sum().sum()),
            "exact_duplicate_rows": int(df.duplicated().sum()),
        })
    return pd.DataFrame(rows)


def build_numeric_profile(tables: dict) -> pd.DataFrame:
    rows = []
    for name, df in tables.items():
        for col in df.select_dtypes(include=np.number).columns:
            s = df[col].dropna()
            if s.empty:
                continue
            rows.append({
                "table": name,
                "column": col,
                "count": len(s),
                "missing": int(df[col].isna().sum()),
                "mean": s.mean(),
                "median": s.median(),
                "p90": s.quantile(.90),
                "p99": s.quantile(.99),
                "min": s.min(),
                "max": s.max(),
            })
    return pd.DataFrame(rows)


def build_missing_report(tables: dict) -> pd.DataFrame:
    rows = []
    for name, df in tables.items():
        for col in df.columns:
            rows.append({
                "table": name,
                "column": col,
                "missing_count": int(df[col].isna().sum()),
                "missing_pct": round(df[col].isna().mean()*100, 3),
            })
    return pd.DataFrame(rows).query("missing_count > 0").sort_values("missing_count", ascending=False)


def run_eda(tables: dict, raw_dir: Path, report_dir: Path):
    report_dir.mkdir(parents=True, exist_ok=True)
    build_inventory(tables, raw_dir).to_csv(report_dir / "raw_inventory.csv", index=False)
    build_numeric_profile(tables).to_csv(report_dir / "numeric_profile.csv", index=False)
    build_missing_report(tables).to_csv(report_dir / "missing_report.csv", index=False)

    for name, df in tables.items():
        cat_rows = []
        for col in df.select_dtypes(include=["object"]).columns:
            if col.endswith("_id") or df[col].nunique(dropna=False) > 30:
                continue
            vc = df[col].value_counts(dropna=False)
            for value, count in vc.items():
                cat_rows.append({
                    "table": name, "column": col, "value": value,
                    "count": int(count), "share_pct": round(count/len(df)*100, 3)
                })
        if cat_rows:
            pd.DataFrame(cat_rows).to_csv(report_dir / f"{name}_value_counts.csv", index=False)
