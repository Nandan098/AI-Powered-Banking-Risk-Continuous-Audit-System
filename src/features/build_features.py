from pathlib import Path
import numpy as np
import pandas as pd

CITY_COORDS = {
    "Mumbai":(19.076,72.878),"Delhi":(28.614,77.209),"Bengaluru":(12.972,77.594),
    "Hyderabad":(17.385,78.487),"Chennai":(13.083,80.270),"Pune":(18.521,73.857),
    "Kolkata":(22.573,88.364),"Ahmedabad":(23.023,72.572),"Jaipur":(26.912,75.787),
    "Lucknow":(26.847,80.946),"Indore":(22.720,75.858),"Bhopal":(23.260,77.412),
    "Surat":(21.170,72.831),"Nagpur":(21.146,79.088),"Chandigarh":(30.733,76.779),
    "Kochi":(9.932,76.267),"Coimbatore":(11.017,76.956),"Vadodara":(22.307,73.181),
}


def haversine_km(city_a, city_b):
    lat1, lon1 = CITY_COORDS.get(city_a, (0,0))
    lat2, lon2 = CITY_COORDS.get(city_b, (0,0))
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2-lat1)
    dlambda = np.radians(lon2-lon1)
    a = np.sin(dphi/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dlambda/2)**2
    return 2*r*np.arcsin(np.sqrt(a))


def _rolling_counts(group: pd.DataFrame, window_minutes: int) -> np.ndarray:
    ts = group["transaction_date"].astype("int64").to_numpy() // 10**9
    window = window_minutes * 60
    result = np.empty(len(ts), dtype=np.int32)
    left = 0
    for i in range(len(ts)):
        while left < i and ts[i] - ts[left] > window:
            left += 1
        result[i] = i - left
    return result


def build_transaction_features(customers, accounts, merchants, customer_devices, transactions):
    tx = transactions.copy()
    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"])
    tx = tx.sort_values(["customer_id", "transaction_date", "transaction_id"]).reset_index(drop=True)

    customer_ref = customers.set_index("customer_id")
    tx["customer_home_city"] = tx["customer_id"].map(customer_ref["city"])
    tx["customer_age"] = tx["customer_id"].map(customer_ref["age"])

    # Behavioral baseline; demographic attributes are kept for context only.
    tx["log_amount"] = np.log1p(tx["amount"])
    tx["customer_median_amount"] = tx.groupby("customer_id")["amount"].transform("median")
    tx["customer_q1_amount"] = tx.groupby("customer_id")["amount"].transform(lambda s: s.quantile(.25))
    tx["customer_q3_amount"] = tx.groupby("customer_id")["amount"].transform(lambda s: s.quantile(.75))
    tx["customer_iqr_amount"] = (tx["customer_q3_amount"] - tx["customer_q1_amount"]).clip(lower=1.0)
    tx["amount_robust_z"] = (
        (tx["amount"] - tx["customer_median_amount"]).abs() /
        (tx["customer_iqr_amount"] * 1.349)
    ).clip(0, 50)
    tx["amount_to_customer_median"] = (
        tx["amount"] / tx["customer_median_amount"].replace(0, np.nan)
    ).replace([np.inf, -np.inf], np.nan).fillna(1.0).clip(0, 10000)

    # Previous-transaction behavior in customer history.
    tx["prior_customer_tx_count"] = tx.groupby("customer_id").cumcount()
    tx["prior_channel_count"] = tx.groupby(["customer_id", "channel"]).cumcount()
    tx["channel_prior_share"] = (
        (tx["prior_channel_count"] + 1) /
        (tx["prior_customer_tx_count"] + tx["channel"].nunique() + 1)
    )
    tx["prior_merchant_category_count"] = tx.groupby(["customer_id", "merchant_category"]).cumcount()
    tx["merchant_category_prior_share"] = (
        (tx["prior_merchant_category_count"] + 1) /
        (tx["prior_customer_tx_count"] + tx["merchant_category"].nunique() + 1)
    )

    tx["minutes_since_prev_tx"] = (
        tx.groupby("customer_id")["transaction_date"].diff().dt.total_seconds().div(60)
    ).fillna(10_000).clip(0, 10_000)

    # Rolling customer velocity.
    tx["tx_count_10m"] = 0
    tx["tx_count_1h"] = 0
    tx["tx_count_24h"] = 0
    for _, idx in tx.groupby("customer_id", sort=False).groups.items():
        group = tx.loc[idx]
        tx.loc[idx, "tx_count_10m"] = _rolling_counts(group, 10)
        tx.loc[idx, "tx_count_1h"] = _rolling_counts(group, 60)
        tx.loc[idx, "tx_count_24h"] = _rolling_counts(group, 24*60)

    tx["tx_count_10m"] = tx["tx_count_10m"].astype(int)
    tx["tx_count_1h"] = tx["tx_count_1h"].astype(int)
    tx["tx_count_24h"] = tx["tx_count_24h"].astype(int)

    # Mobility / context.
    tx["location_distance_km"] = [
        haversine_km(a, b) for a, b in zip(tx["customer_home_city"], tx["location"])
    ]
    tx["location_change"] = (tx["location"] != tx["customer_home_city"]).astype(int)

    # Device novelty in chronological customer history.
    tx["device_seen_before"] = (tx.groupby(["customer_id", "device_id"]).cumcount() > 0).astype(int)
    tx["new_device"] = 1 - tx["device_seen_before"]

    # Near-duplicate candidate within same account and business attributes.
    dup_keys = ["account_id","amount","merchant_id","channel"]
    tx["duplicate_candidate_2min"] = (
        tx.groupby(dup_keys)["transaction_date"].diff().dt.total_seconds().abs().le(120)
        .fillna(False).astype(int)
    )

    # Calendar behavior.
    tx["hour"] = tx["transaction_date"].dt.hour
    tx["day_of_week"] = tx["transaction_date"].dt.dayofweek
    tx["is_weekend"] = tx["day_of_week"].ge(5).astype(int)
    tx["hour_sin"] = np.sin(2*np.pi*tx["hour"]/24)
    tx["hour_cos"] = np.cos(2*np.pi*tx["hour"]/24)

    # Status flags, used for descriptive monitoring but not as direct fraud truth.
    tx["is_success"] = tx["status"].eq("Success").astype(int)
    tx["is_failed_or_reversed"] = tx["status"].isin(["Failed","Reversed"]).astype(int)

    return tx
