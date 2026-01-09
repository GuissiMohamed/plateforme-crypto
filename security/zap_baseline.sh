#!/bin/bash
set -e

TARGET="http://host.docker.internal:8000"
docker run --rm -t owasp/zap2docker-stable zap-baseline.py \
  -t "$TARGET" \
  -r zap_report.html
echo "✅ Rapport généré: zap_report.html"
