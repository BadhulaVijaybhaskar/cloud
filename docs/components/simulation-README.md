# Phase I.8 - Global Simulation Sandbox

## Overview
The Global Simulation Sandbox provides a comprehensive testing environment for ATOM Cloud components with controlled scenario execution, safety validation, and behavior analysis.

## Architecture

### Core Services (6 microservices)
1. **Simulation Engine** (port 9801) - Scenario execution orchestrator
2. **Scenario Builder** (port 9802) - Scenario creation and validation
3. **Safety Validator** (port 9803) - Policy compliance and safety checks
4. **Behavior Analyzer** (port 9804) - AI behavior analysis and bias detection
5. **Resilience Orchestrator** (port 9805) - Fault injection and chaos engineering
6. **Simulation Dashboard API** (port 9806) - Results aggregation and reporting

### Key Features
- **Scenario-Based Testing**: JSON-defined test scenarios with actors and phases
- **Safety Validation**: P1-P15 policy compliance checking
- **Behavior Analysis**: AI bias detection and explainability scoring
- **Chaos Engineering**: Controlled fault injection and recovery testing
- **Simulation Mode**: Full functionality without external dependencies

## Quick Start

### Prerequisites
- Python 3.11+
- FastAPI and dependencies (see requirements.txt)

### Installation
```bash
cd phase-i8
pip install -r requirements.txt
```

### Running Services
```bash
# Start all services (separate terminals)
python services/simulation-engine/main.py
python services/scenario-builder/main.py  
python services/safety-validator/main.py
python services/behavior-analyzer/main.py
python services/resilience-orchestrator/main.py
python services/simulation-dashboard-api/main.py
```

### Running Tests
```bash
# Run precheck
python scripts/precheck.py

# Run integration tests
python tests/test_simulation_integration.py

# Execute simulation scenarios
python scripts/run_simulation.py
```

## Scenarios

### Available Scenarios
1. **Basic Load Test** (`scenarios/basic_load_test.json`)
   - Multi-user load simulation
   - Performance metrics collection
   - Success criteria validation

2. **Chaos Engineering** (`scenarios/chaos_engineering.json`)
   - Fault injection testing
   - System resilience validation
   - Recovery time measurement

3. **AI Behavior Test** (`scenarios/ai_behavior_test.json`)
   - AI agent behavior analysis
   - Bias detection and fairness metrics
   - Adversarial robustness testing

### Scenario Format
```json
{
  "scenario_id": "unique_id",
  "name": "Human readable name",
  "actors": [
    {
      "id": "actor_id",
      "type": "actor_type",
      "config": {}
    }
  ],
  "duration_seconds": 300,
  "phases": [
    {
      "name": "phase_name",
      "duration": 60,
      "actions": ["action1", "action2"]
    }
  ],
  "success_criteria": {},
  "metadata": {
    "simulation": true
  }
}
```

## API Endpoints

### Simulation Engine (9801)
- `POST /run` - Execute scenario
- `GET /status/{run_id}` - Get execution status
- `GET /health` - Health check
- `GET /metrics` - Metrics

### Scenario Builder (9802)
- `POST /scenarios` - Create scenario
- `GET /scenarios/{id}` - Get scenario
- `POST /scenarios/{id}/validate` - Validate scenario

### Safety Validator (9803)
- `POST /validate/event` - Validate event against policies

### Behavior Analyzer (9804)
- `POST /analyze` - Analyze behavior data

### Resilience Orchestrator (9805)
- `POST /inject` - Inject fault
- `POST /rollback` - Rollback fault

### Dashboard API (9806)
- `GET /runs` - List simulation runs
- `GET /runs/{id}/summary` - Get run summary

## Safety & Compliance

### Policy Enforcement
- **P1-P7**: Core ATOM policies (privacy, security, safety, etc.)
- **P13-P15**: Extended simulation policies
- **Real-time Validation**: All events validated before execution
- **Emergency Stop**: Safety kill-switch for critical scenarios

### Safety Measures
- Input validation and sanitization
- Output filtering and monitoring
- Human oversight for high-risk scenarios
- Automatic rollback on safety violations

## Simulation Mode

The system operates in simulation mode when external infrastructure is unavailable:

- **Offline Operation**: Full functionality without external services
- **Synthetic Data**: Realistic test data generation
- **Mock Integrations**: Simulated external API calls
- **Graceful Degradation**: Automatic fallback to simulation

## Monitoring & Reporting

### Generated Reports
- `reports/I.8_precheck.json` - Environment readiness
- `reports/I.8_simulation_report.json` - Scenario execution results
- `reports/I.8_integration_test.json` - Integration test results
- `reports/I.8_behavior_report.json` - Behavior analysis results

### Metrics Collected
- Scenario execution times
- Success/failure rates
- Policy violation counts
- Behavior analysis scores
- System resource usage

## Development

### Adding New Scenarios
1. Create JSON scenario file in `scenarios/`
2. Define actors, phases, and success criteria
3. Add to simulation runner script
4. Test with validation service

### Extending Services
1. Add new endpoints to existing services
2. Implement new analysis algorithms
3. Update integration tests
4. Document API changes

## Production Deployment

### Docker Deployment
```bash
# Build images for each service
docker build -t simulation-engine services/simulation-engine/
docker build -t scenario-builder services/scenario-builder/
# ... etc for all services

# Run with docker-compose
docker-compose up -d
```

### Kubernetes Deployment
```bash
# Apply manifests
kubectl apply -f k8s/
```

### Configuration
- Environment variables for external service URLs
- Policy configuration files
- Scenario template libraries
- Safety threshold settings

## Troubleshooting

### Common Issues
1. **Services not starting**: Check port availability
2. **Validation failures**: Review policy configuration
3. **Scenario errors**: Validate JSON format
4. **Network timeouts**: Increase timeout values

### Debug Commands
```bash
# Check service health
curl http://localhost:9801/health

# Validate scenario
curl -X POST http://localhost:9803/validate/event -d @scenario.json

# View metrics
curl http://localhost:9801/metrics
```

## License
Apache 2.0 - See LICENSE file for details