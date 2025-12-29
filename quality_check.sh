#!/bin/bash
set -e

echo "✅ 1) Tests + coverage"
python -m pytest --cov=backend --cov=collector --cov-report=term-missing --cov-report=xml

echo "✅ 2) (Optionnel) Sonar Scanner"
if command -v sonar-scanner >/dev/null 2>&1; then
  sonar-scanner
else
  echo "⚠ sonar-scanner non installé, skip"
fi

echo "✅ 3) (Optionnel) OWASP ZAP baseline"
if command -v docker >/dev/null 2>&1; then
  ./security/zap_baseline.sh || echo "⚠ ZAP a retourné des alertes (rapport généré si possible)"
else
  echo "⚠ docker non dispo, skip ZAP"
fi

echo "🎉 Qualité terminée."
