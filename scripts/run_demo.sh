#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=src
python scripts/seed_demo.py
exec uvicorn chainbreaker.api.app:app --host 127.0.0.1 --port 8000
