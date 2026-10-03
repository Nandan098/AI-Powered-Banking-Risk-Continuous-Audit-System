import pytest
from src.config import RAW_DIR
from src.io_utils import read_raw_tables
from src.features.build_features import build_transaction_features


@pytest.fixture(scope="module")
def sample_features():
    tables = read_raw_tables(RAW_DIR)
    tx = tables["transactions"].head(5000).copy()
    account_ids = tx["account_id"].unique()
    customer_ids = tx["customer_id"].unique()
    merchant_ids = tx["merchant_id"].unique()
    device_ids = tx["device_id"].unique()
    return build_transaction_features(
        tables["customers"][tables["customers"].customer_id.isin(customer_ids)].copy(),
        tables["accounts"][tables["accounts"].account_id.isin(account_ids)].copy(),
        tables["merchants"][tables["merchants"].merchant_id.isin(merchant_ids)].copy(),
        tables["customer_devices"][tables["customer_devices"].device_id.isin(device_ids)].copy(),
        tx,
    )


def test_feature_row_count_matches_transactions(sample_features):
    assert len(sample_features) == 5000


def test_feature_ids_unique(sample_features):
    assert sample_features["transaction_id"].is_unique


def test_velocity_features_non_negative(sample_features):
    assert (sample_features[["tx_count_10m","tx_count_1h","tx_count_24h"]] >= 0).all().all()
