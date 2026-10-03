from pathlib import Path
import pandas as pd
import numpy as np

PRIMARY_KEYS = {
    "customers":["customer_id"],
    "accounts":["account_id"],
    "merchants":["merchant_id"],
    "customer_devices":["device_id"],
    "transactions":["transaction_id"],
}

DATE_COLUMNS = {
    "customers":["customer_since"],
    "accounts":["opening_date"],
    "customer_devices":["first_seen","last_seen"],
    "transactions":["transaction_date"],
}

NUMERIC_COLUMNS = {
    "customers":["age","annual_income"],
    "accounts":["balance"],
    "transactions":["amount"],
}


def clean_tables(tables: dict, processed_dir: Path):
    """Create a processed layer without modifying the raw data."""
    cleaned = {}
    log = []

    for name, raw in tables.items():
        df = raw.copy()
        before = len(df)

        # Normalize column names and string values.
        df.columns = (
            df.columns.astype(str).str.strip().str.lower()
            .str.replace(r"[^a-z0-9]+", "_", regex=True)
            .str.strip("_")
        )
        for col in df.columns:
            if pd.api.types.is_object_dtype(df[col]):
                df[col] = df[col].astype("string").str.strip()
                df[col] = df[col].replace({"":pd.NA, "nan":pd.NA, "None":pd.NA})

        # Explicit date/numeric parsing.
        for col in DATE_COLUMNS.get(name, []):
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        for col in NUMERIC_COLUMNS.get(name, []):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        exact_removed = int(df.duplicated().sum())
        if exact_removed:
            df = df.drop_duplicates().copy()

        key_cols = PRIMARY_KEYS.get(name, [])
        key_removed = int(df.duplicated(subset=key_cols, keep="first").sum()) if key_cols else 0
        if key_removed:
            df = df.drop_duplicates(subset=key_cols, keep="first").copy()

        # Domain rules: mark invalid values as missing for controlled handling.
        if name == "customers":
            if "age" in df:
                df.loc[~df["age"].between(18,78), "age"] = np.nan
            if "annual_income" in df:
                df.loc[df["annual_income"] <= 0, "annual_income"] = np.nan
        elif name == "accounts" and "balance" in df:
            df.loc[df["balance"] < 0, "balance"] = np.nan
        elif name == "transactions" and "amount" in df:
            df.loc[df["amount"] <= 0, "amount"] = np.nan

        cleaned[name] = df
        df.to_csv(processed_dir / f"{name}.csv", index=False)
        log.append({
            "table":name,
            "rows_before":before,
            "rows_after":len(df),
            "exact_duplicates_removed":exact_removed,
            "duplicate_key_rows_removed":key_removed,
            "missing_cells_after":int(df.isna().sum().sum()),
        })

    return cleaned, pd.DataFrame(log)


def validate_cleaned_tables(tables: dict) -> pd.DataFrame:
    c=tables["customers"]; a=tables["accounts"]; m=tables["merchants"]
    d=tables["customer_devices"]; t=tables["transactions"]
    checks=[]
    def add(name, ok, detail):
        checks.append({"check":name,"passed":bool(ok),"detail":detail})
    add("customers primary key unique", c.customer_id.is_unique, int(c.customer_id.duplicated().sum()))
    add("accounts primary key unique", a.account_id.is_unique, int(a.account_id.duplicated().sum()))
    add("transactions primary key unique", t.transaction_id.is_unique, int(t.transaction_id.duplicated().sum()))
    add("accounts reference customers", a.customer_id.isin(c.customer_id).all(), int((~a.customer_id.isin(c.customer_id)).sum()))
    add("transactions reference accounts", t.account_id.isin(a.account_id).all(), int((~t.account_id.isin(a.account_id)).sum()))
    add("transactions reference merchants", t.merchant_id.isin(m.merchant_id).all(), int((~t.merchant_id.isin(m.merchant_id)).sum()))
    add("transactions reference devices", t.device_id.isin(d.device_id).all(), int((~t.device_id.isin(d.device_id)).sum()))
    add("transaction customer/account consistent", (t.customer_id == t.account_id.map(a.set_index("account_id")["customer_id"])).all(), 0)
    add("transaction amounts positive", (t.amount>0).all(), int((t.amount<=0).sum()))
    opened=t.account_id.map(a.set_index("account_id")["opening_date"])
    add("transaction after account opening", (t.transaction_date>=opened).all(), int((t.transaction_date<opened).sum()))
    add("no missing cells", int(sum(x.isna().sum().sum() for x in tables.values()))==0, int(sum(x.isna().sum().sum() for x in tables.values())))
    return pd.DataFrame(checks)
