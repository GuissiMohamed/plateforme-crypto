#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=${NAMESPACE:-plateforme-crypto}
BACKUP_FILE=${1:-}

if [ -z "${BACKUP_FILE}" ]; then
  echo "Usage: ./infra/restore-db.sh /path/to/backup.sql"
  exit 1
fi

kubectl -n "${NAMESPACE}" exec -i deploy/postgres -- bash -c \
  'psql -U "$POSTGRES_USER" "$POSTGRES_DB"' < "${BACKUP_FILE}"
