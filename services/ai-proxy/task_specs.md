# AI-Proxy Task Specifications

> **AGENT INSTRUCTION:** Always run in `SIMULATION_MODE=true` unless all dependent infrastructure modules are live and verified.
> Never attempt Terraform apply or Helm install in live mode during simulation.

## Environment Variables
```bash
# Simulation Control
SIMULATION_MODE=true  # Agents must run in simulation if infrastructure is missing
COMPONENT_NAME="ai-proxy"
SERVICE_PORT="8081"
```

## H2.1 - AI-Proxy Gateway
**Acceptance Criteria:**
- External API gateway with authentication
- Request routing and load balancing
- Rate limiting and throttling
- Security headers and CORS

**Files to Change:**
- `services/ai-proxy-gateway/main.py`
- `services/ai-proxy-gateway/Dockerfile`
- `services/ai-proxy-gateway/requirements.txt`

**Tests to Add:**
- `tests/ai-proxy/unit/test_gateway_auth.py`
- `tests/ai-proxy/integration/test_request_routing.py`

## H2.2 - AI-Proxy Cache
**Acceptance Criteria:**
- Response caching with TTL
- Cache invalidation strategies
- Memory and Redis backends
- Cache hit/miss metrics

**Files to Change:**
- `services/ai-proxy-cache/main.py`
- `services/ai-proxy-cache/Dockerfile`
- `services/ai-proxy-cache/requirements.txt`

**Tests to Add:**
- `tests/ai-proxy/unit/test_cache_operations.py`
- `tests/ai-proxy/integration/test_cache_backends.py`

## H2.3 - AI-Proxy Router
**Acceptance Criteria:**
- Intelligent request routing
- Service discovery integration
- Health checking and failover
- Circuit breaker patterns

**Files to Change:**
- `services/ai-proxy-router/main.py`
- `services/ai-proxy-router/Dockerfile`
- `services/ai-proxy-router/requirements.txt`

**Tests to Add:**
- `tests/ai-proxy/unit/test_routing_logic.py`
- `tests/ai-proxy/integration/test_service_discovery.py`

## H2.4 - Realtime Integration
**Acceptance Criteria:**
- WebSocket connection management
- Real-time event streaming
- Connection pooling
- Backpressure handling

**Files to Change:**
- `services/realtime-service/main.py`
- `services/realtime-service/Dockerfile`
- `services/realtime-service/requirements.txt`

**Tests to Add:**
- `tests/ai-proxy/unit/test_websocket_handling.py`
- `tests/ai-proxy/integration/test_realtime_streaming.py`

## H2.5 - Infrastructure
**Acceptance Criteria:**
- Helm charts with serviceMesh toggle
- Terraform modules
- Configuration management
- Deployment scripts

**Files to Change:**
- `infra/helm/ai-proxy/Chart.yaml`
- `infra/helm/ai-proxy/values.yaml`
- `infra/terraform/modules/ai-proxy/main.tf`

**Tests to Add:**
- `tests/ai-proxy/e2e/test_deployment.py`
- `tests/ai-proxy/e2e/test_service_mesh.py`