from pathlib import Path
import pandas as pd


def read_raw_tables(raw_dir: Path):
    customers = pd.read_csv(raw_dir / "customers.csv", parse_dates=["customer_since"])
    accounts = pd.read_csv(raw_dir / "accounts.csv", parse_dates=["opening_date"])
    merchants = pd.read_csv(raw_dir / "merchants.csv")
    devices = pd.read_csv(raw_dir / "customer_devices.csv", parse_dates=["first_seen", "last_seen"])
    transactions = pd.read_csv(raw_dir / "transactions.csv", parse_dates=["transaction_date"])
    return {
        "customers": customers,
        "accounts": accounts,
        "merchants": merchants,
        "customer_devices": devices,
        "transactions": transactions,
    }
