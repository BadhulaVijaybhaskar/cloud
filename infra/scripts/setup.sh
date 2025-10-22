#!/bin/bash

# Setup script for development
# Run migrations, apply metadata, etc.

echo "Running setup..."

# Run Prisma migrations
cd backend
npx prisma migrate deploy

# Apply Hasura metadata
../infra/scripts/hasura_apply_metadata.sh

echo "Setup complete."
