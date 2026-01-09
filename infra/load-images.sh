#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME=${CLUSTER_NAME:-plateforme-crypto}
TAG=${TAG:-local}

docker build -t plateforme-crypto-backend:${TAG} backend
docker build -t plateforme-crypto-collector:${TAG} collector
docker build -t plateforme-crypto-frontend:${TAG} frontend

kind load docker-image plateforme-crypto-backend:${TAG} --name "${CLUSTER_NAME}"
kind load docker-image plateforme-crypto-collector:${TAG} --name "${CLUSTER_NAME}"
kind load docker-image plateforme-crypto-frontend:${TAG} --name "${CLUSTER_NAME}"
