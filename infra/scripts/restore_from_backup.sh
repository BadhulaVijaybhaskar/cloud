#!/bin/bash
# Usage: ./restore_from_backup.sh <backup_file>
set -e

BACKUP_FILE=$1
DATABASE_URL=${DATABASE_URL:-"postgresql://naksha:naksha123@localhost:5432/naksha"}

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 /tmp/naksha-backups/backup_2025-10-23_15-30.sql.gz"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file $BACKUP_FILE not found"
    exit 1
fi

echo "Restoring from $BACKUP_FILE ..."
echo "Target database: $DATABASE_URL"

# Extract and restore
gunzip -c "$BACKUP_FILE" | psql "$DATABASE_URL"

echo "Restore completed successfully."