#!/usr/bin/env bash
# ChainBreaker Instant Production / Demo Launcher
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo " CHAINBREAKER · Smart City Incident Reconstruction SOC"
echo " Hackathon ChronoForge · Cybersecurity Track · Team PVR"
echo "=========================================================="

# Find Python 3
if command -v python3 &>/dev/null; then
    PY_BIN=python3
elif command -v python &>/dev/null; then
    PY_BIN=python
else
    echo "[-] Error: Python 3 not found on system PATH."
    exit 1
fi

export PYTHONPATH="src:${PYTHONPATH:-}"

echo "[+] Initializing storage & schema..."
mkdir -p runtime/databases runtime/uploads runtime/reports

echo "[+] Launching ChainBreaker console on http://127.0.0.1:8000"
echo "    - Workbench:        http://127.0.0.1:8000/"
echo "    - Attack Recreator: http://127.0.0.1:8000/recreate"
echo "    - Scenarios:        http://127.0.0.1:8000/scenarios"
echo "    - Database Hub:     http://127.0.0.1:8000/database"
echo "    - Evasion Lab:      http://127.0.0.1:8000/evasion"
echo "    - Benchmarks:       http://127.0.0.1:8000/metrics"
echo "=========================================================="

exec "$PY_BIN" -m uvicorn chainbreaker.api.app:app --host 0.0.0.0 --port 8000 --reload
