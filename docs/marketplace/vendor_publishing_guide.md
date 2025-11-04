# ATOM Marketplace - Vendor Publishing Guide

## Overview
The ATOM Marketplace allows vendors to publish and monetize AI models and agents. This guide covers the publishing process, governance requirements, and revenue sharing.

## Publishing Process

### 1. Model Publishing
```bash
curl -X POST http://localhost:8100/v1/publish/model \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-awesome-model",
    "vendor_id": "vendor-uuid",
    "version": "1.0.0",
    "kind": "model",
    "description": "AI model for text classification",
    "artifact_url": "https://my-storage.com/model.tar.gz",
    "license": "MIT",
    "tags": ["nlp", "classification"],
    "rationale": "Model trained on public datasets",
    "safety_metadata": {
      "bias_tested": true,
      "safety_score": 95
    }
  }'
```

### 2. Agent Publishing
```bash
curl -X POST http://localhost:8102/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "data-analyzer-agent",
    "vendor_id": "vendor-uuid",
    "version": "2.0.0",
    "description": "Autonomous data analysis agent",
    "execution_policy": {
      "max_runtime_seconds": 3600,
      "allowed_actions": ["read_data", "analyze", "generate_report"],
      "resource_limits": {
        "cpu": "2",
        "memory": "4Gi"
      }
    },
    "capabilities": ["data_analysis", "reporting", "visualization"]
  }'
```

## Governance Requirements

### Policy Compliance (P1-P20)
- **P1 Data Privacy**: No PII in model artifacts or metadata
- **P2 Secrets & Signing**: All packages must be cosign-signed
- **P5 Bias Testing**: Models must pass bias validation
- **Security Scanning**: Automated vulnerability scanning required

### Approval Process
1. Submit model/agent for review
2. Automated governance checks (P1-P20)
3. Security scanning and validation
4. Manual review for high-risk categories
5. Approval and marketplace listing

## Revenue Sharing

### Model Sales
- **Vendor Share**: 70% of revenue
- **Platform Fee**: 30% of revenue
- **Payout Schedule**: Monthly automatic payouts
- **Minimum Payout**: $100 USD

### Usage-Based Billing
```json
{
  "project_id": "customer-project",
  "model_id": "your-model-id",
  "units": 1000,
  "cost_center": "ml_inference",
  "timestamp": "2024-12-28T10:00:00Z"
}
```

## Testing and Validation

### Sandbox Testing
```bash
# Test agent in sandbox
curl -X POST http://localhost:8102/v1/agents/{agent_id}/test-run \
  -H "Content-Type: application/json" \
  -d '{
    "test_config": {
      "dataset": "sample_data",
      "timeout": 300
    }
  }'
```

### Quality Metrics
- **Performance Score**: Automated benchmarking
- **Security Score**: Vulnerability assessment
- **Reliability Score**: Uptime and error rates
- **User Ratings**: Community feedback

## Best Practices

### Model Packaging
- Use standard formats (ONNX, TensorFlow SavedModel)
- Include model metadata and documentation
- Provide example usage code
- Test across different environments

### Agent Development
- Follow execution policy guidelines
- Implement proper error handling
- Include comprehensive logging
- Test resource consumption

### Documentation
- Clear description and use cases
- API documentation and examples
- Performance benchmarks
- Known limitations

## Support and Resources

### Developer Support
- **Documentation**: https://docs.atom.cloud/marketplace
- **Community Forum**: https://community.atom.cloud
- **Support Email**: marketplace-support@atom.cloud

### Monitoring and Analytics
- Real-time download metrics
- Revenue tracking dashboard
- User feedback and ratings
- Performance analytics

## Simulation Mode
During development and testing, the marketplace operates in simulation mode:
- No real payments processed
- Simulated governance checks
- Mock artifact storage
- Test data and metrics

Set `SIMULATION_MODE=false` for production deployment.