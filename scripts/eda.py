from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RAW_DIR, REPORT_DIR
from src.io_utils import read_raw_tables
from src.eda.profile import run_eda

if __name__ == "__main__":
    tables = read_raw_tables(RAW_DIR)
    run_eda(tables, RAW_DIR, REPORT_DIR / "eda")
    print(f"EDA reports written to {REPORT_DIR / 'eda'}")
