# Rollback Procedures - H1, H2, H3 Components

## Emergency Rollback Commands

### LangGraph (H1) Rollback
```bash
# Immediate rollback
helm rollback langgraph --namespace langgraph
kubectl scale deployment langgraph-core --replicas=0 -n langgraph

# Restore previous version
helm upgrade langgraph infra/helm/langgraph --set langgraphCore.image.tag=previous-version
```

### AI-Proxy (H2) Rollback  
```bash
# Traffic diversion
kubectl patch service ai-proxy-gateway -p '{"spec":{"selector":{"version":"stable"}}}'
helm rollback ai-proxy --namespace ai-proxy
```

### Workflow-Registry (H3) Rollback
```bash
# Stop new workflows
kubectl scale deployment workflow-registry-core --replicas=0 -n workflow-registry
# Rollback
helm rollback workflow-registry --namespace workflow-registry
```

## Owners
- **Primary**: DevOps Team (devops@atom-cloud.com)
- **Secondary**: Platform Team (platform@atom-cloud.com)
- **Escalation**: CTO (cto@atom-cloud.com)