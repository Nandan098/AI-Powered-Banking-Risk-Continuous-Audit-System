from src.config import RAW_DIR
from src.io_utils import read_raw_tables


def test_referential_integrity():
    t = read_raw_tables(RAW_DIR)
    assert t["accounts"]["customer_id"].isin(t["customers"]["customer_id"]).all()
    assert t["transactions"]["account_id"].isin(t["accounts"]["account_id"]).all()
    assert t["transactions"]["merchant_id"].isin(t["merchants"]["merchant_id"]).all()
    assert t["transactions"]["device_id"].isin(t["customer_devices"]["device_id"]).all()
