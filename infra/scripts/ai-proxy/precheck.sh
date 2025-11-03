#!/bin/bash
set -e
: "${SIMULATION_MODE:=true}"
COMPONENT_NAME="ai-proxy"

echo "Running $COMPONENT_NAME in SIMULATION_MODE=$SIMULATION_MODE"

# AGENT INSTRUCTION: Always run in SIMULATION_MODE=true unless all dependent infrastructure modules are live and verified
# Never attempt Terraform apply or Helm install in live mode during simulation

echo "Precheck for $COMPONENT_NAME SIMULATION_MODE=$SIMULATION_MODE" > reports/$COMPONENT_NAME/precheck.log

# Create reports directory if it doesn't exist
mkdir -p reports/$COMPONENT_NAME

# Check reachable URLs only in live mode
if [ "$SIMULATION_MODE" = "false" ]; then
  echo "Checking live dependencies..." >> reports/$COMPONENT_NAME/precheck.log
  
  # Check LangGraph service
  curl -sSf "${LANGGRAPH_URL:-http://localhost:8080}/health" || {
    echo "ERROR: LangGraph service not reachable" >> reports/$COMPONENT_NAME/precheck.log
    exit 2
  }
  
  # Check Workflow Registry service
  curl -sSf "${WORKFLOW_REGISTRY_URL:-http://localhost:8084}/health" || {
    echo "ERROR: Workflow Registry not reachable" >> reports/$COMPONENT_NAME/precheck.log
    exit 2
  }
  
  # Check Redis for caching
  curl -sSf "${REDIS_URL:-redis://localhost:6379}" || {
    echo "ERROR: Redis not reachable" >> reports/$COMPONENT_NAME/precheck.log
    exit 2
  }
  
  echo "All dependencies reachable" >> reports/$COMPONENT_NAME/precheck.log
else
  echo "SIMULATION_MODE=true - skipping dependency checks" >> reports/$COMPONENT_NAME/precheck.log
fi

# Check required environment variables
required_vars=("COMPONENT_NAME" "SERVICE_PORT" "JWT_SECRET")
for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "WARNING: $var not set, using defaults" >> reports/$COMPONENT_NAME/precheck.log
  else
    echo "$var is set" >> reports/$COMPONENT_NAME/precheck.log
  fi
done

echo "Precheck completed successfully" >> reports/$COMPONENT_NAME/precheck.log
exit 0