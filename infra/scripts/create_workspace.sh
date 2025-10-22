#!/bin/bash

if [ $# -ne 2 ]; then
  echo "Usage: $0 <workspace_name> <owner_email>"
  exit 1
fi

WORKSPACE_NAME=$1
OWNER_EMAIL=$2

# Generate UUID for workspace
WORKSPACE_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')

# Get owner ID
OWNER_ID=$(psql -h postgres -U naksha -d naksha_system -t -c "SELECT id FROM users WHERE email = '$OWNER_EMAIL';" | xargs)

if [ -z "$OWNER_ID" ]; then
  echo "Owner email not found"
  exit 1
fi

# Create workspace in public schema
psql -h postgres -U naksha -d naksha_system -c "INSERT INTO workspaces (id, name, owner_id) VALUES ('$WORKSPACE_ID', '$WORKSPACE_NAME', '$OWNER_ID');"

# Create tenant schema
SCHEMA_NAME="ws_$WORKSPACE_ID"
psql -h postgres -U naksha -d naksha_system -c "CREATE SCHEMA $SCHEMA_NAME;"

# Create tables in tenant schema
psql -h postgres -U naksha -d naksha_system -c "
CREATE TABLE $SCHEMA_NAME.projects (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  description text,
  created_by uuid,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE $SCHEMA_NAME.items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES $SCHEMA_NAME.projects(id),
  data jsonb,
  created_at timestamptz DEFAULT now()
);
"

if [ "$ENABLE_PGVECTOR" = "true" ]; then
  psql -h postgres -U naksha -d naksha_system -c "
  CREATE EXTENSION IF NOT EXISTS vector;
  CREATE TABLE $SCHEMA_NAME.embeddings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id uuid,
    text_chunk text,
    vector vector
  );
  "
fi

echo "Workspace created: $WORKSPACE_ID"
