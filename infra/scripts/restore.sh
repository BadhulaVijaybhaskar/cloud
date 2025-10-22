#!/bin/bash

# Naksha Cloud Restore Script
set -e

BACKUP_DATE="$1"
S3_BUCKET="${BACKUP_S3_BUCKET:-naksha-backups}"
RESTORE_DIR="/tmp/restore"

if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: $0 <backup_date>"
    echo "Available backups:"
    aws s3 ls "s3://$S3_BUCKET/" --recursive | grep -o '[0-9]\{8\}_[0-9]\{6\}' | sort -u
    exit 1
fi

echo "Starting restore process for backup: $BACKUP_DATE"

# Download backup from S3
mkdir -p "$RESTORE_DIR"
aws s3 sync "s3://$S3_BUCKET/$BACKUP_DATE/" "$RESTORE_DIR/"

# Restore Postgres
echo "Restoring Postgres..."
psql "$DATABASE_URL" < "$RESTORE_DIR/postgres_backup.sql"

# Restore Milvus
echo "Restoring Milvus..."
kubectl exec -n vector deployment/milvus -- tar xzf - -C / < "$RESTORE_DIR/milvus_backup.tar.gz"

# Restore Vault
echo "Restoring Vault..."
kubectl cp "$RESTORE_DIR/vault_snapshot.snap" vault/vault-0:/tmp/vault_snapshot.snap
kubectl exec -n vault vault-0 -- vault operator raft snapshot restore /tmp/vault_snapshot.snap

# Cleanup
rm -rf "$RESTORE_DIR"

echo "Restore completed successfully at $(date)"