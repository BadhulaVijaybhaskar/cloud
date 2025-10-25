#!/bin/bash

echo "=== Naksha Cloud Structure Validation ==="
echo "Timestamp: $(date)"

# Check core directories
echo "Checking directory structure..."

directories=(
    "services/langgraph"
    "services/vector"
    "services/auth"
    "services/realtime"
    "admin"
    "infra/helm"
    "infra/terraform"
    "infra/vault"
    "infra/monitoring"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir: Directory exists"
    else
        echo "❌ $dir: Directory missing"
    fi
done

# Check key files
echo "Checking key configuration files..."

files=(
    "docker-compose.dev.yml"
    "services/langgraph/Dockerfile"
    "services/vector/Dockerfile"
    "infra/helm/langgraph/Chart.yaml"
    "infra/terraform/main.tf"
    ".env.example"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file: File exists"
    else
        echo "❌ $file: File missing"
    fi
done

echo "=== Structure Validation Complete ==="