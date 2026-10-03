@echo off
python scripts\run_pipeline.py
pytest -q
