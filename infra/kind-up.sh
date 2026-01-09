#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME=${CLUSTER_NAME:-plateforme-crypto}

kind create cluster --name "${CLUSTER_NAME}" --config infra/kind-config.yaml
