from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import run_pipeline

if __name__ == "__main__":
    summary = run_pipeline()
    print("PIPELINE COMPLETE")
    print("=" * 60)
    for key, value in summary.items():
        print(f"{key}: {value}")
