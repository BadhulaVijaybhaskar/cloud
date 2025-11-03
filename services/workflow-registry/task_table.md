# Workflow-Registry High-Level Tasks

| ID | Component | Purpose |
|----|-----------|---------|
| H.3.1 | workflow-registry-core | Workflow definition storage and validation |
| H.3.2 | workflow-registry-api | CRUD operations for workflow management |
| H.3.3 | realtime-bridge | Event bus integration and workflow triggers |
| H.3.4 | workflow-executor | Workflow execution coordination |
| H.3.5 | infra/helm/workflow-registry | Helm charts with event bus configuration |
| H.3.6 | tests/workflow-registry | Workflow execution and integration tests |

## Integration Points
- **H.1 (langgraph)**: Graph-based workflow execution
- **H.2 (ai-proxy)**: External workflow trigger endpoints
- **Event Bus**: Redis/Kafka for workflow event handling
- **Storage**: PostgreSQL for workflow definitions and state

## Dependencies
- Event bus (Redis/Kafka) for workflow triggers
- PostgreSQL for workflow persistence
- LangGraph for graph-based workflow execution
- Service mesh (optional, helm toggle)