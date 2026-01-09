#!/bin/bash

# OWASP ZAP baseline scan wrapper
# Usage: ./security_zap.sh [TARGET]
# Example: ./security_zap.sh http://localhost:8000

set -euo pipefail
TARGET=${1:-http://localhost:8000}
OUT_DIR="$(pwd)/results/security"
REPORT_HTML="zap_report.html"
REPORT_JSON="zap_report.json"

mkdir -p "$OUT_DIR"

echo "🔐 Lancement OWASP ZAP baseline scan sur $TARGET"

echo "• Les rapports seront sauvegardés dans: $OUT_DIR"

# If running on macOS and target uses localhost, use host.docker.internal
SCAN_TARGET="$TARGET"
if [[ "$(uname)" == "Darwin" ]] && [[ "$TARGET" == *"localhost"* ]]; then
  SCAN_TARGET="${TARGET//localhost/host.docker.internal}"
  echo "ℹ️ macOS détecté — utilisation de $SCAN_TARGET pour que le conteneur puisse atteindre l'hôte"
fi

# Ensure docker daemon is available
if ! command -v docker &> /dev/null; then
  echo "❌ Docker non trouvé. Installez Docker Desktop et relancez le script."
  exit 1
fi

if ! docker info > /dev/null 2>&1; then
  echo "❌ Le démon Docker ne répond pas. Vérifiez que Docker est démarré."
  exit 1
fi

# Try to pull the image first to give clearer errors. If stable fails, try weekly.
IMAGE_STABLE="owasp/zap2docker-stable"
IMAGE_WEEKLY="owasp/zap2docker-weekly"
echo "ℹ️ Tentative de pull de l'image Docker $IMAGE_STABLE (peut demander login)"
if docker pull "$IMAGE_STABLE":latest; then
  IMAGE="$IMAGE_STABLE"
elif docker pull "$IMAGE_WEEKLY":latest; then
  IMAGE="$IMAGE_WEEKLY"
  echo "ℹ️ Utilisation de l'image alternative: $IMAGE_WEEKLY"
else
  echo "⚠️ Échec du pull des images $IMAGE_STABLE et $IMAGE_WEEKLY. Vérifiez votre connexion à Docker Hub ou exécutez 'docker login'."
  echo "Vous pouvez aussi installer ZAP localement (Homebrew Cask) ou télécharger les outils de scan manuellement."
  echo "Options recommandées:"
  echo "  1) docker login && re-essayez"
  echo "  2) brew install --cask owasp-zap (macOS) puis utilisez l'interface GUI ou scripts locaux"
  exit 1
fi

# Run ZAP baseline
echo "ℹ️ Lancement du conteneur $IMAGE pour exécuter zap-baseline.py"
docker run --rm -v "$OUT_DIR":/zap/wrk/:rw "$IMAGE" \
  zap-baseline.py -t "$SCAN_TARGET" -r "$REPORT_HTML" -J "$REPORT_JSON" -z "-config api.disablekey=true" -v

if [ -f "$OUT_DIR/$REPORT_HTML" ]; then
  echo "✅ Rapport HTML: $OUT_DIR/$REPORT_HTML"
fi
if [ -f "$OUT_DIR/$REPORT_JSON" ]; then
  echo "✅ Rapport JSON: $OUT_DIR/$REPORT_JSON"
fi

echo "🔎 Conseils: ouvrez le HTML pour inspecter les findings. Corrigez les vulnérabilités critiques en priorité."
