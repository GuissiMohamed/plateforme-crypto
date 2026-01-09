#!/usr/bin/env bash
set -euo pipefail

# Usage: ./stop_locust.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping Locust processes..."
pkill -f "locust -f locustfile.py" || true
sleep 1
pkill -9 -f "locust -f locustfile.py" || true

echo "Remaining locust processes:" 
ps aux | grep locust | grep -v grep || true
echo "Done."
