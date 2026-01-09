#!/bin/bash

# Snyk scan wrapper for Python projects
# Usage: export SNYK_TOKEN=... && ./security_snyk.sh

set -euo pipefail
OUT_DIR="$(pwd)/results/security"
mkdir -p "$OUT_DIR"

if ! command -v snyk &> /dev/null; then
  echo "⚠️  'snyk' CLI non trouvé. Installez-le: npm i -g snyk"
  exit 1
fi

# Authenticate if token provided
if [ -n "${SNYK_TOKEN:-}" ]; then
  echo "🔐 Auth Snyk via SNYK_TOKEN"
  snyk auth "$SNYK_TOKEN" || true
fi

# Run snyk test on requirements.txt (if present)
REQ_FILE="backend/requirements.txt"
if [ -f "$REQ_FILE" ]; then
  echo "🔎 Lancement Snyk test sur $REQ_FILE"
  snyk test --file="$REQ_FILE" --json > "$OUT_DIR/snyk_results.json" || true
  echo "✅ Résultats sauvegardés: $OUT_DIR/snyk_results.json"
  echo "🔔 Vous pouvez aussi envoyer un snapshot: snyk monitor --file=$REQ_FILE"
else
  echo "⚠️  Aucun requirements.txt trouvé à $REQ_FILE. Vous pouvez exécuter 'snyk test' manuellement dans le répertoire approprié."
fi
