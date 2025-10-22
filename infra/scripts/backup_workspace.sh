#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <workspace_id>"
  exit 1
fi

WORKSPACE_ID=$1
DATE=$(date +%Y%m%d)
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

SCHEMA_NAME="ws_$WORKSPACE_ID"
BACKUP_FILE="$BACKUP_DIR/${SCHEMA_NAME}_$DATE.sql"

pg_dump -h postgres -U naksha -d naksha_system --schema=$SCHEMA_NAME > $BACKUP_FILE

echo "Backup created: $BACKUP_FILE"
