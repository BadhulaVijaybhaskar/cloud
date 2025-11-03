# Workflow-Registry Task Specifications

> **AGENT INSTRUCTION:** Always run in `SIMULATION_MODE=true` unless all dependent infrastructure modules are live and verified.
> Never attempt Terraform apply or Helm install in live mode during simulation.

## Environment Variables
```bash
# Simulation Control
SIMULATION_MODE=true  # Agents must run in simulation if infrastructure is missing
COMPONENT_NAME="workflow-registry"
SERVICE_PORT="8084"
```

## H3.1 - Workflow Registry Core
**Acceptance Criteria:**
- Workflow metadata storage and retrieval
- Version management and rollback
- Workflow validation and schema checking
- Search and discovery APIs

**Files to Change:**
- `services/workflow-registry-core/main.py`
- `services/workflow-registry-core/Dockerfile`
- `services/workflow-registry-core/requirements.txt`

**Tests to Add:**
- `tests/workflow-registry/unit/test_registry_core.py`
- `tests/workflow-registry/integration/test_workflow_crud.py`

## H3.2 - Workflow Registry API
**Acceptance Criteria:**
- REST API for workflow operations
- Authentication and authorization
- API versioning and documentation
- Rate limiting and validation

**Files to Change:**
- `services/workflow-registry-api/main.py`
- `services/workflow-registry-api/Dockerfile`
- `services/workflow-registry-api/requirements.txt`

**Tests to Add:**
- `tests/workflow-registry/unit/test_api_endpoints.py`
- `tests/workflow-registry/integration/test_workflow_api.py`

## H3.3 - Realtime Bridge
**Acceptance Criteria:**
- Event bus integration
- Real-time workflow triggers
- Event filtering and routing
- Backpressure and retry logic

**Files to Change:**
- `services/realtime-bridge/main.py`
- `services/realtime-bridge/Dockerfile`
- `services/realtime-bridge/requirements.txt`

**Tests to Add:**
- `tests/workflow-registry/unit/test_realtime_bridge.py`
- `tests/workflow-registry/integration/test_event_processing.py`

## H3.4 - Workflow Execution
**Acceptance Criteria:**
- Workflow execution engine
- State management and persistence
- Error handling and recovery
- Execution monitoring and logging

**Files to Change:**
- `services/workflow-registry/main.py`
- `services/workflow-registry/Dockerfile`
- `services/workflow-registry/requirements.txt`

**Tests to Add:**
- `tests/workflow-registry/unit/test_workflow_execution.py`
- `tests/workflow-registry/integration/test_execution_engine.py`

## H3.5 - Infrastructure
**Acceptance Criteria:**
- Helm charts with serviceMesh toggle
- Terraform modules
- Configuration management
- Deployment scripts

**Files to Change:**
- `infra/helm/workflow-registry/Chart.yaml`
- `infra/helm/workflow-registry/values.yaml`
- `infra/terraform/modules/workflow-registry/main.tf`

**Tests to Add:**
- `tests/workflow-registry/e2e/test_deployment.py`
- `tests/workflow-registry/e2e/test_service_mesh.py`