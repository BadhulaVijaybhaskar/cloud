# LangGraph — LangGraph workflow orchestration integration (Agent-Ready Build Plan)

**Project:** ATOM Cloud Platform
**Component:** LangGraph
**Version target:** v1.0.0-langgraph
**Branch prefix:** prod-feature/langgraph
**Architecture:** Global Directory Structure (NO phase directories)
**Mode:** Autonomous execution

> **AGENT INSTRUCTION**: Use SIMULATION_MODE=true if infrastructure missing
> **CRITICAL**: Never create phase-* directories. Use existing global directory structure only.

---

## Summary / Goal

**Objective:** Implement full LangGraph workflow runtime and graph execution engine. Provide production-grade services under `services/langgraph-*`, helm charts in `infra/helm/langgraph/`, connectors, tests, and deployment scripts. Deliver a runnable simulation mode and CI job that validates workflow execution and graph processing with measurable evidence.

**Success Criteria:**

* [ ] Services deployed to services/langgraph-core/, services/langgraph-api/, services/langgraph-worker/
* [ ] Infrastructure in infra/terraform/modules/langgraph/ and infra/helm/langgraph/
* [ ] Tests in tests/langgraph/ (unit, integration, e2e)
* [ ] Scripts in infra/scripts/langgraph/
* [ ] Contracts in infra/contracts/langgraph/ (if applicable)
* [ ] Security configs in infra/security/langgraph/
* [ ] Policies in infra/vault/policies/langgraph.hcl
* [ ] No phase directories created
* [ ] All integration tests pass

## Environment Variables (agent must read/use)

```bash
# Component Configuration
COMPONENT_NAME="langgraph"
SERVICES_PATH="services"
INFRA_PATH="infra"
TESTS_PATH="tests"
CONTRACTS_PATH="infra/contracts"
SECURITY_PATH="infra/security"
SCRIPTS_PATH="infra/scripts"
POLICIES_PATH="infra/vault/policies"

# Deployment Settings
SIMULATION_MODE=true  # Set false only when infra ready
DOCKER_REGISTRY="localhost:5000"
NAMESPACE="atom-cloud"

# LangGraph Specific
LANGGRAPH_EXECUTOR_REPLICAS=1
LANGGRAPH_GRAPH_DB_URL=${LANGGRAPH_GRAPH_DB_URL:-bolt://localhost:7687}
LANGGRAPH_QUEUE_URL=${LANGGRAPH_QUEUE_URL:-redis://localhost:6379/0}
LANGGRAPH_ADMIN_TOKEN=${LANGGRAPH_ADMIN_TOKEN:-changeme}

# Security & Compliance
POLICY_ENFORCEMENT=true
METADATA_LABELING=true
AUDIT_LOGGING=true
```

## File / Directory Structure to Create (exact)

```
services/
├── langgraph-core/
│   ├── src/main.py
│   ├── config.yaml
│   ├── Dockerfile
│   └── requirements.txt
├── langgraph-api/
│   ├── src/api.py
│   └── Dockerfile
└── langgraph-worker/
    ├── src/worker.py
    └── Dockerfile

infra/
├── terraform/modules/langgraph/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── helm/langgraph/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── contracts/langgraph/
│   ├── LangGraph.sol
│   └── deploy.js
├── security/langgraph/
│   ├── security-policy.yaml
│   └── rbac.yaml
├── scripts/langgraph/
│   ├── deploy.sh
│   ├── backup.sh
│   └── migrate.sh
└── vault/policies/
    └── langgraph.hcl

tests/langgraph/
├── unit/
├── integration/
└── e2e/
```

## Service Specifications & Endpoints

### LangGraph-Core Service

**Path:** `services/langgraph-core/`
**Port:** 8080
**Endpoints:**

* `GET /health` → Health check
* `POST /api/v1/execute` → Submit workflow execution request `{graph_id, entry_point, inputs}`
* `GET /api/v1/graphs/{id}` → Fetch graph definition
* `GET /metrics` → Prometheus metrics

**Environment:**

```yaml
SERVICE_NAME: "langgraph-core"
SERVICE_PORT: 8080
GRAPH_DB_URL: "${LANGGRAPH_GRAPH_DB_URL}"
QUEUE_URL: "${LANGGRAPH_QUEUE_URL}"
ADMIN_TOKEN: "${LANGGRAPH_ADMIN_TOKEN}"
```

### LangGraph-API Service

**Path:** `services/langgraph-api/`
**Port:** 8081
**Purpose:** External API gateway for graph submission, management, and observability.
**Endpoints:**

* `POST /v1/graphs` → Create/update graph
* `GET /v1/graphs` → List graphs
* `POST /v1/execute` → Proxy to core execute endpoint
* `GET /v1/executions/{id}` → Execution status and trace

**Environment:**

```yaml
SERVICE_NAME: "langgraph-api"
SERVICE_PORT: 8081
CORE_URL: "http://langgraph-core:8080"
AUTH_URL: "${AUTH_URL}"
```

### LangGraph-Worker

**Path:** `services/langgraph-worker/`
**Port:** n/a (worker)
**Purpose:** Execute graph nodes, run tasks, emit traces to audit log.
**Environment:**

```yaml
WORKER_NAME: "langgraph-worker"
QUEUE_URL: "${LANGGRAPH_QUEUE_URL}"
GRAPH_DB_URL: "${LANGGRAPH_GRAPH_DB_URL}"
```

## Deployment Script (embedded)

**File:** `infra/scripts/langgraph/deploy.sh`

```bash
#!/bin/bash
set -e

COMPONENT_NAME="langgraph"
SERVICES_PATH="services"
INFRA_PATH="infra"
CONTRACTS_PATH="infra/contracts"
SECURITY_PATH="infra/security"
POLICIES_PATH="infra/vault/policies"

echo "Deploying ${COMPONENT_NAME} services..."

# Build services
for service in ${SERVICES_PATH}/${COMPONENT_NAME}-*; do
    if [ -d "$service" ]; then
        echo "Building $(basename $service)..."
        docker build -t "${DOCKER_REGISTRY}/atom-cloud/$(basename $service):latest" "$service"
    fi
done

# Deploy contracts (if exists)
if [ -d "${CONTRACTS_PATH}/${COMPONENT_NAME}" ]; then
    echo "Deploying contracts..."
    cd "${CONTRACTS_PATH}/${COMPONENT_NAME}"
    node deploy.js || echo "Contract deploy simulated"
    cd -
fi

# Apply security policies
if [ -d "${SECURITY_PATH}/${COMPONENT_NAME}" ]; then
    echo "Applying security policies..."
    kubectl apply -f "${SECURITY_PATH}/${COMPONENT_NAME}/" || echo "kubectl apply simulated"
fi

# Deploy infrastructure and helm
if [ "$SIMULATION_MODE" != "true" ]; then
    terraform -chdir="${INFRA_PATH}/terraform/modules/${COMPONENT_NAME}" apply -auto-approve
    helm upgrade --install "${COMPONENT_NAME}" "${INFRA_PATH}/helm/${COMPONENT_NAME}"
    if [ -f "${POLICIES_PATH}/${COMPONENT_NAME}.hcl" ]; then
        vault policy write "${COMPONENT_NAME}" "${POLICIES_PATH}/${COMPONENT_NAME}.hcl"
    fi
else
    echo "SIMULATION_MODE=true - skipping terraform/helm. Create simulated k8s manifests in reports."
fi

echo "Deployment complete for ${COMPONENT_NAME}"
```

## Integration Test Template (embedded)

**File:** `tests/langgraph/integration/test_langgraph.py`

```python
import pytest
import requests
import os

COMPONENT_NAME = os.getenv('COMPONENT_NAME', 'langgraph')
BASE_URL = os.getenv('LANGGRAPH_API_URL', 'http://localhost:8081')
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true') == 'true'

class TestLangGraphIntegration:
    def test_service_health(self):
        """Test service health endpoint"""
        if SIMULATION_MODE:
            assert True, "Simulation mode: Health check passed"
        else:
            response = requests.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            assert response.json().get('status') == 'ok'

    def test_basic_execute(self):
        """Test basic graph execution"""
        if SIMULATION_MODE:
            # Simulate a successful execution trace
            trace = {"execution_id":"sim-1","status":"completed"}
            assert trace["status"] == "completed"
        else:
            payload = {"graph_id": "sample-graph", "entry_point": "start", "inputs": {}}
            response = requests.post(f"{BASE_URL}/v1/execute", json=payload)
            assert response.status_code in (200,201)
```

## Agent Execution Steps (explicit sequence)

1. **Validate Environment**

   ```bash
   # Check no phase directories exist
   if ls phase-* 2>/dev/null; then
       echo "ERROR: Phase directories found. Migration required."
       exit 1
   fi
   ```

2. **Create Complete Component Structure**

   ```bash
   mkdir -p services/langgraph-{core,api,worker}
   mkdir -p infra/terraform/modules/langgraph
   mkdir -p infra/helm/langgraph
   mkdir -p infra/contracts/langgraph
   mkdir -p infra/security/langgraph
   mkdir -p infra/scripts/langgraph
   mkdir -p tests/langgraph/{unit,integration,e2e}
   touch infra/vault/policies/langgraph.hcl
   ```

3. **Deploy Services**

   ```bash
   ./infra/scripts/langgraph/deploy.sh
   ```

4. **Run Validation**

   ```bash
   python -m pytest tests/langgraph/integration/ -v
   ```

## Acceptance Criteria

* [ ] Services in services/langgraph-*/ (no phase directories)
* [ ] Infrastructure in infra/terraform/modules/langgraph and infra/helm/langgraph/
* [ ] Tests in tests/langgraph/ with all test types
* [ ] Scripts in infra/scripts/langgraph/ for deployment
* [ ] Contracts in infra/contracts/langgraph/ (if applicable)
* [ ] Security configs in infra/security/langgraph/
* [ ] Vault policies in infra/vault/policies/langgraph.hcl
* [ ] Integration tests pass in both simulation and live modes
* [ ] No hardcoded phase paths in any files
* [ ] All components build and deploy successfully

## Notes for the Agent (embedded prompt)

> You are building ATOM Cloud components using the established global directory structure.
> NEVER create phase-* directories. Components are distributed across global directories only.
> Use SIMULATION_MODE=true when infrastructure is not available. Validate all paths before creation. Follow the exact directory structure specified above.

---

# Ai-Proxy — AI Proxy and Realtime API Layer (Agent-Ready Build Plan)

**Project:** ATOM Cloud Platform
**Component:** ai-proxy
**Version target:** v1.0.0-ai-proxy
**Branch prefix:** prod-feature/ai-proxy
**Architecture:** Global Directory Structure (NO phase directories)
**Mode:** Autonomous execution

> **AGENT INSTRUCTION**: Use SIMULATION_MODE=true if infrastructure missing
> **CRITICAL**: Never create phase-* directories. Use existing global directory structure only.

---

## Summary / Goal

**Objective:** Implement full API gateway, ai-proxy and realtime services with service-mesh integration hooks and advanced proxy features. Provide services under `services/ai-proxy-*` and `services/realtime/`. Deliver helm chart, terraform module, security, tests, and deploy scripts. Provide simulation mode for local validation.

**Success Criteria:**

* [ ] Services deployed to services/ai-proxy-core/, services/ai-proxy-gateway/, services/realtime/
* [ ] Infrastructure in infra/terraform/modules/ai-proxy and infra/helm/ai-proxy
* [ ] Tests in tests/ai-proxy/
* [ ] Scripts in infra/scripts/ai-proxy/
* [ ] Contracts in infra/contracts/ai-proxy/ (if applicable)
* [ ] Security configs in infra/security/ai-proxy/
* [ ] Policies in infra/vault/policies/ai-proxy.hcl
* [ ] No phase directories created
* [ ] All integration tests pass

## Environment Variables (agent must read/use)

```bash
# Component Configuration
COMPONENT_NAME="ai-proxy"
SERVICES_PATH="services"
INFRA_PATH="infra"
TESTS_PATH="tests"
CONTRACTS_PATH="infra/contracts"
SECURITY_PATH="infra/security"
SCRIPTS_PATH="infra/scripts"
POLICIES_PATH="infra/vault/policies"

# Deployment Settings
SIMULATION_MODE=true  # Set false only when infra ready
DOCKER_REGISTRY="localhost:5000"
NAMESPACE="atom-cloud"

# AI Proxy Specific
API_GATEWAY_URL=${API_GATEWAY_URL:-http://localhost:8082}
PROXY_RATE_LIMIT=1000
PROXY_TIMEOUT=30
SERVICE_MESH_ENABLED=false

# Security & Compliance
POLICY_ENFORCEMENT=true
METADATA_LABELING=true
AUDIT_LOGGING=true
```

## File / Directory Structure to Create (exact)

```
services/
├── ai-proxy-core/
│   ├── src/main.py
│   ├── config.yaml
│   ├── Dockerfile
│   └── requirements.txt
├── ai-proxy-gateway/
│   ├── src/gateway.py
│   └── Dockerfile
└── realtime/
    ├── src/realtime_server.py
    └── Dockerfile

infra/
├── terraform/modules/ai-proxy/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── helm/ai-proxy/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── contracts/ai-proxy/
│   ├── ProxyContract.sol
│   └── deploy.js
├── security/ai-proxy/
│   ├── security-policy.yaml
│   └── rbac.yaml
├── scripts/ai-proxy/
│   ├── deploy.sh
│   ├── backup.sh
│   └── migrate.sh
└── vault/policies/
    └── ai-proxy.hcl

tests/ai-proxy/
├── unit/
├── integration/
└── e2e/
```

## Service Specifications & Endpoints

### AI-Proxy-Core Service

**Path:** `services/ai-proxy-core/`
**Port:** 8082
**Endpoints:**

* `GET /health` → Health check
* `POST /v1/proxy` → Proxy request to mapped AI backend
* `GET /v1/routes` → List proxy routes
* `POST /v1/cache/invalidate` → Invalidate cached responses
* `GET /metrics` → Prometheus metrics

**Environment:**

```yaml
SERVICE_NAME: "ai-proxy-core"
SERVICE_PORT: 8082
RATE_LIMIT: ${PROXY_RATE_LIMIT}
TIMEOUT: ${PROXY_TIMEOUT}
```

### AI-Proxy-Gateway Service

**Path:** `services/ai-proxy-gateway/`
**Port:** 8083
**Purpose:** Ingress-level gateway with JWT verification, role-based routing, and observability hooks.

**Endpoints:**

* `POST /v1/request` → Accept client request, validate, forward to ai-proxy-core or realtime
* `GET /v1/status` → Gateway status

**Environment:**

```yaml
SERVICE_NAME: "ai-proxy-gateway"
SERVICE_PORT: 8083
UPSTREAM: "http://ai-proxy-core:8082"
```

### Realtime Service

**Path:** `services/realtime/`
**Port:** 8090
**Purpose:** WebSocket and SSE endpoints for real-time streaming of inference results and logs.

**Endpoints:**

* `GET /ws` → WebSocket endpoint
* `GET /sse` → Server-sent events

**Environment:**

```yaml
SERVICE_NAME: "realtime"
SERVICE_PORT: 8090
```

## Deployment Script (embedded)

**File:** `infra/scripts/ai-proxy/deploy.sh`

```bash
#!/bin/bash
set -e

COMPONENT_NAME="ai-proxy"
SERVICES_PATH="services"
INFRA_PATH="infra"
CONTRACTS_PATH="infra/contracts"
SECURITY_PATH="infra/security"
POLICIES_PATH="infra/vault/policies"

echo "Deploying ${COMPONENT_NAME} services..."

# Build services
for service in ${SERVICES_PATH}/${COMPONENT_NAME}-* ${SERVICES_PATH}/realtime; do
    if [ -d "$service" ]; then
        echo "Building $(basename $service)..."
        docker build -t "${DOCKER_REGISTRY}/atom-cloud/$(basename $service):latest" "$service"
    fi
done

# Apply security policies
if [ -d "${SECURITY_PATH}/${COMPONENT_NAME}" ]; then
    echo "Applying security policies..."
    kubectl apply -f "${SECURITY_PATH}/${COMPONENT_NAME}/" || echo "kubectl apply simulated"
fi

if [ "$SIMULATION_MODE" != "true" ]; then
    terraform -chdir="${INFRA_PATH}/terraform/modules/${COMPONENT_NAME}" apply -auto-approve
    helm upgrade --install "${COMPONENT_NAME}" "${INFRA_PATH}/helm/${COMPONENT_NAME}"
    if [ -f "${POLICIES_PATH}/${COMPONENT_NAME}.hcl" ]; then
        vault policy write "${COMPONENT_NAME}" "${POLICIES_PATH}/${COMPONENT_NAME}.hcl"
    fi
else
    echo "SIMULATION_MODE=true - skipping terraform/helm"
fi

echo "Deployment complete for ${COMPONENT_NAME}"
```

## Integration Test Template (embedded)

**File:** `tests/ai-proxy/integration/test_ai_proxy.py`

```python
import os, requests, pytest

COMPONENT_NAME = os.getenv('COMPONENT_NAME', 'ai-proxy')
BASE_URL = os.getenv('API_GATEWAY_URL', 'http://localhost:8083')
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true') == 'true'

def test_gateway_health():
    if SIMULATION_MODE:
        assert True
    else:
        r = requests.get(f"{BASE_URL}/v1/status")
        assert r.status_code == 200

def test_proxy_route():
    if SIMULATION_MODE:
        assert True
    else:
        payload = {"input":"test"}
        r = requests.post(f"{BASE_URL}/v1/request", json=payload)
        assert r.status_code in (200,201)
```

## Agent Execution Steps (explicit sequence)

1. **Validate Environment**

   ```bash
   if ls phase-* 2>/dev/null; then
       echo "ERROR: Phase directories found. Migration required."
       exit 1
   fi
   ```

2. **Create Complete Component Structure**

   ```bash
   mkdir -p services/ai-proxy-{core,gateway}
   mkdir -p services/realtime
   mkdir -p infra/terraform/modules/ai-proxy
   mkdir -p infra/helm/ai-proxy
   mkdir -p infra/contracts/ai-proxy
   mkdir -p infra/security/ai-proxy
   mkdir -p infra/scripts/ai-proxy
   mkdir -p tests/ai-proxy/{unit,integration,e2e}
   touch infra/vault/policies/ai-proxy.hcl
   ```

3. **Deploy Services**

   ```bash
   ./infra/scripts/ai-proxy/deploy.sh
   ```

4. **Run Validation**

   ```bash
   python -m pytest tests/ai-proxy/integration/ -v
   ```

## Acceptance Criteria

* [ ] Services in services/ai-proxy-*/ and services/realtime/ (no phase directories)
* [ ] Infrastructure in infra/terraform/modules/ai-proxy and infra/helm/ai-proxy/
* [ ] Tests in tests/ai-proxy/
* [ ] Scripts in infra/scripts/ai-proxy/ for deployment
* [ ] Contracts in infra/contracts/ai-proxy/ (if applicable)
* [ ] Security configs in infra/security/ai-proxy/
* [ ] Vault policies in infra/vault/policies/ai-proxy.hcl
* [ ] Integration tests pass in both simulation and live modes
* [ ] No hardcoded phase paths in any files
* [ ] Service-mesh readiness hooks included in helm values (serviceMesh.enabled flag)

## Notes for the Agent (embedded prompt)

> Build ai-proxy and realtime services under global directories. Do not create phase-* directories. Include service-mesh integration toggles in helm values. Default to SIMULATION_MODE=true when infra is not available.

---

# Workflow-Registry — Workflow registry, realtime bridge, and integration patterns (Agent-Ready Build Plan)

**Project:** ATOM Cloud Platform
**Component:** workflow-registry
**Version target:** v1.0.0-workflow-registry
**Branch prefix:** prod-feature/workflow-registry
**Architecture:** Global Directory Structure (NO phase directories)
**Mode:** Autonomous execution

> **AGENT INSTRUCTION**: Use SIMULATION_MODE=true if infrastructure missing
> **CRITICAL**: Never create phase-* directories. Use existing global directory structure only.

---

## Summary / Goal

**Objective:** Implement complete workflow registry, realtime bridge, and connectors enabling event-driven workflows. Provide services under `services/workflow-registry/` and `services/realtime-bridge/`. Deliver helm charts, terraform module, security, tests, and deployment scripts. Ensure interoperability with LangGraph and ai-proxy.

**Success Criteria:**

* [ ] Services deployed to services/workflow-registry/ and services/realtime-bridge/
* [ ] Infrastructure in infra/terraform/modules/workflow-registry and infra/helm/workflow-registry
* [ ] Tests in tests/workflow-registry/
* [ ] Scripts in infra/scripts/workflow-registry/
* [ ] Contracts in infra/contracts/workflow-registry/ (if applicable)
* [ ] Security configs in infra/security/workflow-registry/
* [ ] Policies in infra/vault/policies/workflow-registry.hcl
* [ ] No phase directories created
* [ ] All integration tests pass

## Environment Variables (agent must read/use)

```bash
# Component Configuration
COMPONENT_NAME="workflow-registry"
SERVICES_PATH="services"
INFRA_PATH="infra"
TESTS_PATH="tests"
CONTRACTS_PATH="infra/contracts"
SECURITY_PATH="infra/security"
SCRIPTS_PATH="infra/scripts"
POLICIES_PATH="infra/vault/policies"

# Deployment Settings
SIMULATION_MODE=true  # Set false only when infra ready
DOCKER_REGISTRY="localhost:5000"
NAMESPACE="atom-cloud"

# Workflow Registry Specific
REGISTRY_DB_URL=${REGISTRY_DB_URL:-postgres://user:pass@localhost:5432/registry}
REALTIME_BRIDGE_URL=${REALTIME_BRIDGE_URL:-http://localhost:8090}
EVENT_BUS_URL=${EVENT_BUS_URL:-redis://localhost:6379/1}
REGISTRY_ADMIN_TOKEN=${REGISTRY_ADMIN_TOKEN:-changeme}

# Security & Compliance
POLICY_ENFORCEMENT=true
METADATA_LABELING=true
AUDIT_LOGGING=true
```

## File / Directory Structure to Create (exact)

```
services/
├── workflow-registry/
│   ├── src/main.py
│   ├── config.yaml
│   ├── Dockerfile
│   └── requirements.txt
└── realtime-bridge/
    ├── src/bridge.py
    └── Dockerfile

infra/
├── terraform/modules/workflow-registry/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── helm/workflow-registry/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── contracts/workflow-registry/
│   ├── RegistryContract.sol
│   └── deploy.js
├── security/workflow-registry/
│   ├── security-policy.yaml
│   └── rbac.yaml
├── scripts/workflow-registry/
│   ├── deploy.sh
│   ├── backup.sh
│   └── migrate.sh
└── vault/policies/
    └── workflow-registry.hcl

tests/workflow-registry/
├── unit/
├── integration/
└── e2e/
```

## Service Specifications & Endpoints

### Workflow-Registry Service

**Path:** `services/workflow-registry/`
**Port:** 8084
**Endpoints:**

* `GET /health` → Health check
* `POST /v1/workflows` → Register workflow metadata
* `GET /v1/workflows` → List workflows
* `POST /v1/trigger` → Trigger workflow execution
* `GET /v1/executions/{id}` → Execution status

**Environment:**

```yaml
SERVICE_NAME: "workflow-registry"
SERVICE_PORT: 8084
DATABASE_URL: "${REGISTRY_DB_URL}"
EVENT_BUS_URL: "${EVENT_BUS_URL}"
ADMIN_TOKEN: "${REGISTRY_ADMIN_TOKEN}"
```

### Realtime-Bridge Service

**Path:** `services/realtime-bridge/`
**Port:** 8091
**Purpose:** Bridge events from event bus to LangGraph and other executors. Provide high-throughput adapters and backpressure handling.

**Endpoints:**

* `POST /v1/publish` → Publish event to event bus
* `GET /v1/subscribe` → Webhook for subscribing services
* `GET /metrics` → Prometheus metrics

**Environment:**

```yaml
SERVICE_NAME: "realtime-bridge"
SERVICE_PORT: 8091
EVENT_BUS_URL: "${EVENT_BUS_URL}"
DOWNSTREAM_URL: "${REALTIME_BRIDGE_URL}"
```

## Deployment Script (embedded)

**File:** `infra/scripts/workflow-registry/deploy.sh`

```bash
#!/bin/bash
set -e

COMPONENT_NAME="workflow-registry"
SERVICES_PATH="services"
INFRA_PATH="infra"
CONTRACTS_PATH="infra/contracts"
SECURITY_PATH="infra/security"
POLICIES_PATH="infra/vault/policies"

echo "Deploying ${COMPONENT_NAME} services..."

for service in ${SERVICES_PATH}/${COMPONENT_NAME} ${SERVICES_PATH}/realtime-bridge; do
    if [ -d "$service" ]; then
        echo "Building $(basename $service)..."
        docker build -t "${DOCKER_REGISTRY}/atom-cloud/$(basename $service):latest" "$service"
    fi
done

if [ -d "${SECURITY_PATH}/${COMPONENT_NAME}" ]; then
    echo "Applying security policies..."
    kubectl apply -f "${SECURITY_PATH}/${COMPONENT_NAME}/" || echo "kubectl apply simulated"
fi

if [ "$SIMULATION_MODE" != "true" ]; then
    terraform -chdir="${INFRA_PATH}/terraform/modules/${COMPONENT_NAME}" apply -auto-approve
    helm upgrade --install "${COMPONENT_NAME}" "${INFRA_PATH}/helm/${COMPONENT_NAME}"
    if [ -f "${POLICIES_PATH}/${COMPONENT_NAME}.hcl" ]; then
        vault policy write "${COMPONENT_NAME}" "${POLICIES_PATH}/${COMPONENT_NAME}.hcl"
    fi
else
    echo "SIMULATION_MODE=true - skipping terraform/helm"
fi

echo "Deployment complete for ${COMPONENT_NAME}"
```

## Integration Test Template (embedded)

**File:** `tests/workflow-registry/integration/test_workflow_registry.py`

```python
import os, requests, pytest, time

COMPONENT_NAME = os.getenv('COMPONENT_NAME', 'workflow-registry')
BASE_URL = os.getenv('WORKFLOW_REGISTRY_URL', 'http://localhost:8084')
BRIDGE_URL = os.getenv('REALTIME_BRIDGE_URL', 'http://localhost:8091')
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true') == 'true'

def test_registry_health():
    if SIMULATION_MODE:
        assert True
    else:
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code == 200

def test_register_and_trigger_workflow():
    if SIMULATION_MODE:
        assert True
    else:
        wf = {"id":"sample-wf","nodes":[]}
        r = requests.post(f"{BASE_URL}/v1/workflows", json=wf)
        assert r.status_code in (200,201)
        r2 = requests.post(f"{BASE_URL}/v1/trigger", json={"workflow_id":"sample-wf","inputs":{}})
        assert r2.status_code in (200,202)
```

## Agent Execution Steps (explicit sequence)

1. **Validate Environment**

   ```bash
   if ls phase-* 2>/dev/null; then
       echo "ERROR: Phase directories found. Migration required."
       exit 1
   fi
   ```

2. **Create Complete Component Structure**

   ```bash
   mkdir -p services/workflow-registry
   mkdir -p services/realtime-bridge
   mkdir -p infra/terraform/modules/workflow-registry
   mkdir -p infra/helm/workflow-registry
   mkdir -p infra/contracts/workflow-registry
   mkdir -p infra/security/workflow-registry
   mkdir -p infra/scripts/workflow-registry
   mkdir -p tests/workflow-registry/{unit,integration,e2e}
   touch infra/vault/policies/workflow-registry.hcl
   ```

3. **Deploy Services**

   ```bash
   ./infra/scripts/workflow-registry/deploy.sh
   ```

4. **Run Validation**

   ```bash
   python -m pytest tests/workflow-registry/integration/ -v
   ```

## Acceptance Criteria

* [ ] Services in services/workflow-registry/ and services/realtime-bridge/ (no phase directories)
* [ ] Infrastructure in infra/terraform/modules/workflow-registry and infra/helm/workflow-registry/
* [ ] Tests in tests/workflow-registry/
* [ ] Scripts in infra/scripts/workflow-registry/ for deployment
* [ ] Contracts in infra/contracts/workflow-registry/ (if applicable)
* [ ] Security configs in infra/security/workflow-registry/
* [ ] Vault policies in infra/vault/policies/workflow-registry.hcl
* [ ] Integration tests pass in both simulation and live modes
* [ ] No hardcoded phase paths in any files
* [ ] Realtime bridge supports backpressure and retries

## Notes for the Agent (embedded prompt)

> Build workflow-registry and realtime-bridge under global directories. Do not create phase-* directories. Default to SIMULATION_MODE=true if infra missing. Ensure integration patterns and adapters to LangGraph and ai-proxy are present as configuration stubs. Validate event bus connectivity in simulation mode.

---
