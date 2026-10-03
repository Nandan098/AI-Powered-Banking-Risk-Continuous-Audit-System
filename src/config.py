from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
REFERENCE_DIR = DATA_DIR / "reference"
PROCESSED_DIR = DATA_DIR / "processed"
POWERBI_DIR = DATA_DIR / "powerbi"
REPORT_DIR = DATA_DIR / "reports"
MODEL_DIR = PROJECT_ROOT / "models"

for directory in [PROCESSED_DIR, POWERBI_DIR, REPORT_DIR, MODEL_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = int(os.getenv("RANDOM_STATE", "42"))
MODEL_CONTAMINATION = float(os.getenv("MODEL_CONTAMINATION", "0.015"))
HIGH_RISK_THRESHOLD = float(os.getenv("HIGH_RISK_THRESHOLD", "0.75"))
MEDIUM_RISK_THRESHOLD = float(os.getenv("MEDIUM_RISK_THRESHOLD", "0.60"))
TRAIN_END = os.getenv("TRAIN_END", "2025-01-01")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://banking:banking@localhost:5432/banking_risk"
)
