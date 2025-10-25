#!/bin/bash
# Restore workflow_runs and insight_signals tables

set -e

BACKUP_FILE="$1"

if [ -z "${BACKUP_FILE}" ]; then
  echo "Usage: $0 <backup_file>"
  exit 1
fi

echo "Restoring from backup: ${BACKUP_FILE}"

# Decompress if needed
if [[ "${BACKUP_FILE}" == *.gz ]]; then
  gunzip -c "${BACKUP_FILE}" | psql "${POSTGRES_DSN}"
else
  psql "${POSTGRES_DSN}" < "${BACKUP_FILE}"
fi

echo "Restore completed successfully"