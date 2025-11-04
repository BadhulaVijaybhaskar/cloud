#!/bin/bash
# ATOM Marketplace - Publish Sample Model Script
# Demonstrates model publishing workflow per J.3 spec

set -euo pipefail
: "${SIMULATION_MODE:=true}"
: "${MARKETPLACE_CORE_URL:=http://localhost:8100}"

echo "🚀 Publishing sample model to ATOM Marketplace"
echo "SIMULATION_MODE: ${SIMULATION_MODE}"
echo "Marketplace URL: ${MARKETPLACE_CORE_URL}"

# Sample model metadata
SAMPLE_MODEL='{
  "name": "sample-neural-optimizer",
  "vendor_id": "550e8400-e29b-41d4-a716-446655440000",
  "version": "1.0.0",
  "kind": "model",
  "description": "Sample AI model for performance optimization and neural network tuning",
  "artifact_url": "https://storage.atom.cloud/samples/neural-optimizer-1.0.0.tar.gz",
  "license": "MIT",
  "tags": ["ai", "optimization", "neural", "sample"],
  "rationale": "Demonstrates marketplace publishing workflow with governance compliance",
  "safety_metadata": {
    "bias_tested": true,
    "pii_scanned": true,
    "security_validated": true,
    "sample_model": true
  }
}'

echo "📦 Publishing model with metadata:"
echo "$SAMPLE_MODEL" | jq .

# Publish model
echo "🔄 Sending publish request..."
RESPONSE=$(curl -s -X POST "${MARKETPLACE_CORE_URL}/v1/publish/model" \
  -H "Content-Type: application/json" \
  -d "$SAMPLE_MODEL" \
  -w "HTTP_STATUS:%{http_code}" || echo "HTTP_STATUS:000")

HTTP_STATUS=$(echo "$RESPONSE" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed 's/HTTP_STATUS:[0-9]*$//')

echo "📊 Response Status: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "202" ] || [ "$HTTP_STATUS" = "200" ]; then
  echo "✅ Model published successfully!"
  echo "$BODY" | jq .
  
  # Extract job ID for status checking
  JOB_ID=$(echo "$BODY" | jq -r '.job_id // empty')
  
  if [ -n "$JOB_ID" ]; then
    echo "🔍 Checking job status: $JOB_ID"
    
    # Wait a moment for processing
    sleep 2
    
    # Check job status
    STATUS_RESPONSE=$(curl -s "${MARKETPLACE_CORE_URL}/v1/jobs/${JOB_ID}" || echo '{"error": "failed to check status"}')
    echo "📋 Job Status:"
    echo "$STATUS_RESPONSE" | jq .
  fi
  
else
  echo "❌ Publish failed with status: $HTTP_STATUS"
  echo "$BODY"
  exit 1
fi

# Test model registry integration
echo "🔍 Checking model registry..."
REGISTRY_RESPONSE=$(curl -s "${MARKETPLACE_CORE_URL/8100/8101}/v1/models" || echo '{"error": "registry unavailable"}')
echo "📚 Registry Response:"
echo "$REGISTRY_RESPONSE" | jq .

# Save results to reports
mkdir -p reports
echo "$RESPONSE" > reports/sample_model_publish_response.json
echo "$REGISTRY_RESPONSE" > reports/sample_model_registry_check.json

echo "✅ Sample model publish workflow completed!"
echo "📁 Results saved to reports/"