#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <workspace_id>"
  exit 1
fi

WORKSPACE_ID=$1

# Assuming we add a suspended column to workspaces table
psql -h postgres -U naksha -d naksha_system -c "UPDATE workspaces SET suspended = true WHERE id = '$WORKSPACE_ID';"

echo "Workspace suspended: $WORKSPACE_ID"
