#!/usr/bin/env bash
set -euo pipefail

# Usage: ./start_locust.sh [--port PORT] [--headless] [--users N] [--spawn R] [--time DURATION]
# Defaults: PORT=8090, HEADLESS=no, USERS=100, SPAWN=10, TIME=3m

PORT=8090
HEADLESS=0
USERS=100
SPAWN=10
TIME="3m"
LOG="$HOME/locust_nohup.log"
CSV_DIR="results/performance"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port) PORT="$2"; shift 2;;
    --headless) HEADLESS=1; shift;;
    --users) USERS="$2"; shift 2;;
    --spawn) SPAWN="$2"; shift 2;;
    --time) TIME="$2"; shift 2;;
    -h|--help) echo "Usage: $0 [--port PORT] [--headless] [--users N] [--spawn R] [--time DURATION]"; exit 0;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
cd backend

mkdir -p ../${CSV_DIR}

echo "Stopping existing Locust processes..."
pkill -f "locust -f locustfile.py" || true
sleep 1
pkill -9 -f "locust -f locustfile.py" || true

if [[ $HEADLESS -eq 1 ]]; then
  echo "Starting Locust in headless mode: users=$USERS spawn=$SPAWN time=$TIME"
  locust -f locustfile.py --host=http://localhost:8000 --headless -u ${USERS} -r ${SPAWN} -t ${TIME} --csv=../${CSV_DIR}/locust_run
  exit 0
else
  echo "Starting Locust UI on port ${PORT}, logs -> ${LOG}"
  nohup locust -f locustfile.py --host=http://localhost:8000 --web-port ${PORT} --csv=../${CSV_DIR}/locust_run </dev/null >"${LOG}" 2>&1 &
  disown
  echo "Locust started. Open http://localhost:${PORT}"
fi
