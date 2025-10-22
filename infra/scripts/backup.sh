#!/bin/bash

# Naksha Cloud Backup Script
set -e

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
S3_BUCKET="${BACKUP_S3_BUCKET:-naksha-backups}"

echo "Starting backup process at $(date)"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_DATE"

# Backup Postgres
echo "Backing up Postgres..."
pg_dump "$DATABASE_URL" > "$BACKUP_DIR/$BACKUP_DATE/postgres_backup.sql"

# Backup Milvus data
echo "Backing up Milvus..."
kubectl exec -n vector deployment/milvus -- tar czf - /var/lib/milvus > "$BACKUP_DIR/$BACKUP_DATE/milvus_backup.tar.gz"

# Backup Vault data
echo "Backing up Vault..."
kubectl exec -n vault vault-0 -- vault operator raft snapshot save /tmp/vault_snapshot.snap
kubectl cp vault/vault-0:/tmp/vault_snapshot.snap "$BACKUP_DIR/$BACKUP_DATE/vault_snapshot.snap"

# Upload to S3
echo "Uploading to S3..."
aws s3 sync "$BACKUP_DIR/$BACKUP_DATE" "s3://$S3_BUCKET/$BACKUP_DATE/"

# Cleanup local backups older than 7 days
find "$BACKUP_DIR" -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed successfully at $(date)"