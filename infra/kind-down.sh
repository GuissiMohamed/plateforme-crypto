#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME=${CLUSTER_NAME:-plateforme-crypto}
kind delete cluster --name "${CLUSTER_NAME}"
