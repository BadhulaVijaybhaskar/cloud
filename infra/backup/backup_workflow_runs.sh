#!/bin/bash
# Backup workflow_runs and insight_signals tables

set -e

BACKUP_DIR="${BACKUP_DIR:-/tmp/atom-backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/atom_backup_${TIMESTAMP}.sql"

mkdir -p "${BACKUP_DIR}"

echo "Starting ATOM database backup..."

# Backup specific tables
pg_dump "${POSTGRES_DSN}" \
  --table=workflow_runs \
  --table=insight_signals \
  --table=audit_logs \
  --data-only \
  --inserts > "${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_FILE}"

echo "Backup completed: ${BACKUP_FILE}.gz"

# Upload to S3 if configured
if [ -n "${S3_BACKUP_BUCKET}" ]; then
  aws s3 cp "${BACKUP_FILE}.gz" "s3://${S3_BACKUP_BUCKET}/backups/"
  echo "Backup uploaded to S3"
fi