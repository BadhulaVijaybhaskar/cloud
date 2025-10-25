#!/bin/bash
set -e

echo "=== Naksha Cloud Health Check ==="
echo "Timestamp: $(date)"

# Check if services are running locally
echo "Checking local services..."

# Test LangGraph health (if running)
if curl -s http://localhost:8081/healthz > /dev/null 2>&1; then
    echo "✅ LangGraph: $(curl -s http://localhost:8081/healthz)"
else
    echo "❌ LangGraph: Service not reachable"
fi

# Test Vector service health (if running)
if curl -s http://localhost:8082/healthz > /dev/null 2>&1; then
    echo "✅ Vector Service: $(curl -s http://localhost:8082/healthz)"
else
    echo "❌ Vector Service: Service not reachable"
fi

# Test Admin UI (if running)
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Admin UI: Reachable"
else
    echo "❌ Admin UI: Service not reachable"
fi

# Test Auth service (if running)
if curl -s http://localhost:9999/health > /dev/null 2>&1; then
    echo "✅ Auth Service: $(curl -s http://localhost:9999/health)"
else
    echo "❌ Auth Service: Service not reachable"
fi

# Test Realtime service (if running)
if curl -s http://localhost:4000/health > /dev/null 2>&1; then
    echo "✅ Realtime Service: $(curl -s http://localhost:4000/health)"
else
    echo "❌ Realtime Service: Service not reachable"
fi

echo "=== Health Check Complete ==="