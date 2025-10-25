#!/bin/bash
# Naksha Cloud Quick Start

echo "🚀 Starting Naksha Cloud locally..."

# Copy environment file
cp .env.example .env

# Start all services
docker-compose -f docker-compose.dev.yml up --build -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "✅ Naksha Cloud is running!"
echo ""
echo "🌐 Access Points:"
echo "  Admin UI:     http://localhost:3000"
echo "  Hasura:       http://localhost:8080"
echo "  MinIO:        http://localhost:9001"
echo "  Auth API:     http://localhost:9999"
echo "  Realtime:     ws://localhost:4000"
echo "  LangGraph:    http://localhost:8081"
echo "  Vector API:   http://localhost:8082"
echo ""
echo "🔑 Default Credentials:"
echo "  Admin UI:     admin@naksha.test / password"
echo "  MinIO:        minioadmin / minioadmin"
echo "  Hasura:       admin-secret"