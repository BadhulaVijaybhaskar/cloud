#!/bin/bash

echo "Starting ATOM - Adaptive Topology Orchestration Module"
echo "====================================================="
echo ""

echo "Port Configuration:"
echo "- Landing Page (Vite):    http://localhost:3001"
echo "- Admin UI (Next.js):     http://localhost:3000"
echo "- GraphQL API (Hasura):   http://localhost:8080"
echo "- Auth Service:           http://localhost:9999"
echo "- Realtime Service:       ws://localhost:4000"
echo "- LangGraph Service:      http://localhost:8081"
echo "- Vector Service:         http://localhost:8082"
echo "- MinIO Storage:          http://localhost:9000"
echo "- MinIO Console:          http://localhost:9001"
echo "- PostgreSQL:             localhost:5432"
echo "- Redis:                  localhost:6379"
echo "- Milvus:                 localhost:19530"
echo "- etcd:                   localhost:2379"
echo ""

echo "Building and starting all services..."
docker-compose up --build -d

echo ""
echo "Waiting for services to start..."
sleep 10

echo ""
echo "Service Status:"
docker-compose ps

echo ""
echo "====================================================="
echo "ATOM Platform is starting up!"
echo ""
echo "Access points:"
echo "- Landing Page: http://localhost:3001"
echo "- Admin Dashboard: http://localhost:3000"
echo "- GraphQL Playground: http://localhost:8080/console"
echo "- MinIO Console: http://localhost:9001"
echo ""
echo "Press Ctrl+C to stop following logs..."
echo ""

docker-compose logs -f