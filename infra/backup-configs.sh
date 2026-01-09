#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=${NAMESPACE:-plateforme-crypto}
OUTPUT_DIR=${OUTPUT_DIR:-backups}

mkdir -p "${OUTPUT_DIR}"

kubectl -n "${NAMESPACE}" get configmap -o yaml > "${OUTPUT_DIR}/configmaps.yaml"
kubectl -n "${NAMESPACE}" get secret -o yaml > "${OUTPUT_DIR}/secrets.yaml"
