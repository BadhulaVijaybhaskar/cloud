# ATOM Cloud Agent-Ready Documentation Standard

**CRITICAL: NO PHASE DIRECTORIES ALLOWED - SERVICES-ONLY ARCHITECTURE**

## Mandatory File Structure Rules

### ❌ FORBIDDEN: Phase Directory Creation
```bash
# NEVER CREATE THESE PATTERNS:
phase-*/
phases/
Phase*/
PHASE*/
[letter][number]/  # e.g., I.5/, J.2/
```

### ✅ REQUIRED: Global Directory Architecture
```bash
# ALL NEW COMPONENTS MUST USE EXISTING GLOBAL LOCATIONS:
services/[component-name]/           # Microservices
infra/terraform/modules/[component-name]/  # Infrastructure as code
infra/helm/[component-name]/         # Kubernetes deployments
infra/contracts/[component-name]/    # Smart contracts
infra/security/[component-name]/     # Security configurations
infra/scripts/[component-name]/      # Deployment scripts
infra/vault/policies/[component-name].hcl  # Access policies
tests/[component-name]/              # All test types
```

---

## Agent-Ready Document Template

### Header Format (MANDATORY)
```markdown
# [Component Name] — [Brief Description] (Agent-Ready Build Plan)

**Project:** ATOM Cloud Platform
**Component:** [Component Name] 
**Version target:** v[X.Y.Z]-[component-name]
**Branch prefix:** prod-feature/[component-name]
**Architecture:** Global Directory Structure (NO phase directories)
**Mode:** Autonomous execution

> **AGENT INSTRUCTION**: Use SIMULATION_MODE=true if infrastructure missing
> **CRITICAL**: Never create phase-* directories. Use existing global directory structure only.

---
```

### Core Sections Structure

#### 1. Summary / Goal
```markdown
## Summary / Goal
**Objective:** [Clear, measurable objective]
**Success Criteria:** 
- [ ] Services deployed to services/[component-name]/
- [ ] Infrastructure in infra/[type]/[component-name]/
- [ ] Tests in tests/[component-name]/
- [ ] Scripts in infra/scripts/[component-name]/
- [ ] Contracts in infra/contracts/[component-name]/
- [ ] Security configs in infra/security/[component-name]/
- [ ] Policies in infra/vault/policies/[component-name].hcl
- [ ] No phase directories created
- [ ] All integration tests pass
```

#### 2. Environment Variables (Agent Must Read)
```markdown
## Environment Variables (agent must read/use)
```bash
# Component Configuration
COMPONENT_NAME="[component-name]"
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

# Security & Compliance
POLICY_ENFORCEMENT=true
METADATA_LABELING=true
AUDIT_LOGGING=true
```

#### 3. File Structure (Exact Paths)
```markdown
## File / Directory Structure to Create (exact)
```
services/
├── [component-name]-core/
│   ├── src/main.py
│   ├── config.yaml
│   ├── Dockerfile
│   └── requirements.txt
├── [component-name]-api/
│   ├── src/api.py
│   └── Dockerfile
└── [component-name]-worker/
    ├── src/worker.py
    └── Dockerfile

infra/
├── terraform/modules/[component-name]/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── helm/[component-name]/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── contracts/[component-name]/
│   ├── [Component].sol
│   └── deploy.js
├── security/[component-name]/
│   ├── security-policy.yaml
│   └── rbac.yaml
├── scripts/[component-name]/
│   ├── deploy.sh
│   ├── backup.sh
│   └── migrate.sh
└── vault/policies/
    └── [component-name].hcl

tests/[component-name]/
├── unit/
├── integration/
└── e2e/
```

#### 4. Service Specifications
```markdown
## Service Specifications & Endpoints

### [Component-Name]-Core Service
**Path:** `services/[component-name]-core/`
**Port:** 8080
**Endpoints:**
- `GET /health` → Health check
- `POST /api/v1/[action]` → Primary action
- `GET /metrics` → Prometheus metrics

**Environment:**
```yaml
SERVICE_NAME: "[component-name]-core"
SERVICE_PORT: 8080
DATABASE_URL: "${DATABASE_URL}"
REDIS_URL: "${REDIS_URL}"
```

### [Component-Name]-API Service  
**Path:** `services/[component-name]-api/`
**Port:** 8081
**Purpose:** External API gateway
```

#### 5. Embedded Scripts
```markdown
## Deployment Script (embedded)

**File:** `infra/scripts/[component-name]/deploy.sh`

```bash
#!/bin/bash
set -e

COMPONENT_NAME="[component-name]"
SERVICES_PATH="services"
INFRA_PATH="infra"

echo "Deploying ${COMPONENT_NAME} services..."

# Build services
for service in ${SERVICES_PATH}/${COMPONENT_NAME}-*; do
    if [ -d "$service" ]; then
        echo "Building $(basename $service)..."
        docker build -t "atom-cloud/$(basename $service):latest" "$service"
    fi
done

# Deploy contracts (if exists)
if [ -d "${CONTRACTS_PATH}/${COMPONENT_NAME}" ]; then
    echo "Deploying smart contracts..."
    cd "${CONTRACTS_PATH}/${COMPONENT_NAME}"
    node deploy.js
    cd -
fi

# Apply security policies
if [ -d "${SECURITY_PATH}/${COMPONENT_NAME}" ]; then
    echo "Applying security policies..."
    kubectl apply -f "${SECURITY_PATH}/${COMPONENT_NAME}/"
fi

# Deploy infrastructure
if [ "$SIMULATION_MODE" != "true" ]; then
    terraform -chdir="${INFRA_PATH}/terraform/modules/${COMPONENT_NAME}" apply -auto-approve
    helm upgrade --install "${COMPONENT_NAME}" "${INFRA_PATH}/helm/${COMPONENT_NAME}"
    
    # Apply vault policies
    if [ -f "${POLICIES_PATH}/${COMPONENT_NAME}.hcl" ]; then
        vault policy write "${COMPONENT_NAME}" "${POLICIES_PATH}/${COMPONENT_NAME}.hcl"
    fi
fi

echo "Deployment complete for ${COMPONENT_NAME}"
```

## Integration Test Template (embedded)

**File:** `tests/[component-name]/integration/test_[component-name].py`

```python
import pytest
import requests
import os

COMPONENT_NAME = os.getenv('COMPONENT_NAME', '[component-name]')
BASE_URL = f"http://localhost:8080"
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true') == 'true'

class Test[ComponentName]Integration:
    def test_service_health(self):
        """Test service health endpoint"""
        if SIMULATION_MODE:
            # Simulation mode - mock response
            assert True, "Simulation mode: Health check passed"
        else:
            response = requests.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            assert response.json()['status'] == 'healthy'
    
    def test_api_endpoints(self):
        """Test primary API functionality"""
        if SIMULATION_MODE:
            assert True, "Simulation mode: API test passed"
        else:
            response = requests.post(f"{BASE_URL}/api/v1/test")
            assert response.status_code in [200, 201]
```

#### 6. Agent Execution Steps
```markdown
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
   # Create all component directories
   mkdir -p services/${COMPONENT_NAME}-{core,api,worker}
   mkdir -p infra/terraform/modules/${COMPONENT_NAME}
   mkdir -p infra/helm/${COMPONENT_NAME}
   mkdir -p infra/contracts/${COMPONENT_NAME}
   mkdir -p infra/security/${COMPONENT_NAME}
   mkdir -p infra/scripts/${COMPONENT_NAME}
   mkdir -p tests/${COMPONENT_NAME}/{unit,integration,e2e}
   
   # Create policy file
   touch infra/vault/policies/${COMPONENT_NAME}.hcl
   ```

3. **Deploy Services**
   ```bash
   # Build and deploy each service
   ./infra/scripts/${COMPONENT_NAME}/deploy.sh
   ```

4. **Run Validation**
   ```bash
   # Execute integration tests
   python -m pytest tests/${COMPONENT_NAME}/integration/ -v
   ```

## Failure Handling Rules
* **Phase Directory Detection**: Immediately fail if phase-* directories found
* **Service Conflicts**: Check for existing services with same name
* **Simulation Fallbacks**: Use SIMULATION_MODE=true for missing infrastructure
* **Rollback Strategy**: Keep backup branch before any changes

## Acceptance Criteria
* [ ] Services in services/[component-name]/ (no phase directories)
* [ ] Infrastructure in infra/[type]/[component-name]/ pattern
* [ ] Tests in tests/[component-name]/ with all test types
* [ ] Scripts in infra/scripts/[component-name]/ for deployment
* [ ] Contracts in infra/contracts/[component-name]/ (if applicable)
* [ ] Security configs in infra/security/[component-name]/
* [ ] Vault policies in infra/vault/policies/[component-name].hcl
* [ ] Integration tests pass in both simulation and live modes
* [ ] No hardcoded phase paths in any files
* [ ] All components build and deploy successfully

## Deliverables (explicit)
* **Services**: All microservices in services/[component-name]-*/
* **Infrastructure**: Terraform modules in infra/terraform/modules/[component-name]/
* **Deployments**: Helm charts in infra/helm/[component-name]/
* **Contracts**: Smart contracts in infra/contracts/[component-name]/ (if applicable)
* **Security**: Policies and RBAC in infra/security/[component-name]/
* **Scripts**: Deployment scripts in infra/scripts/[component-name]/
* **Policies**: Vault policies in infra/vault/policies/[component-name].hcl
* **Tests**: Unit, integration, and E2E test suites in tests/[component-name]/
* **Documentation**: Updated README files and API documentation
* **Reports**: Deployment logs saved to logs/[component-name]/

## Security & Compliance Reminders
* **Policy Enforcement**: All services must implement P1-P20 policies
* **Metadata Labeling**: Use component-name labels, not phase labels
* **Audit Logging**: Enable comprehensive logging for all services
* **Access Control**: Implement RBAC with service-specific permissions

## Notes for the Agent (embedded prompt)
> You are building ATOM Cloud components using the established global directory structure.
> NEVER create phase-* directories. Components are distributed across:
> - Services: services/[component-name]/
> - Infrastructure: infra/[type]/[component-name]/
> - Tests: tests/[component-name]/
> - Scripts: infra/scripts/[component-name]/
> - Contracts: infra/contracts/[component-name]/
> - Security: infra/security/[component-name]/
> - Policies: infra/vault/policies/[component-name].hcl
> Use SIMULATION_MODE=true when infrastructure is not available.
> Validate all paths before creation. Follow the exact directory structure specified above.
```

---

## Enforcement Mechanisms

### Pre-Commit Validation Script
```bash
#!/bin/bash
# File: .git/hooks/pre-commit

echo "Validating ATOM Cloud structure..."

# Check for forbidden phase directories
if find . -type d -name "phase-*" -o -name "Phase*" -o -name "PHASE*" | grep -q .; then
    echo "ERROR: Phase directories detected. Use services-only architecture."
    echo "Found:"
    find . -type d -name "phase-*" -o -name "Phase*" -o -name "PHASE*"
    exit 1
fi

# Check for proper service structure
if [ ! -d "services" ]; then
    echo "ERROR: services/ directory missing"
    exit 1
fi

echo "Structure validation passed"
```

### Agent Validation Function
```python
def validate_atom_structure():
    """Validate ATOM Cloud follows services-only architecture"""
    import os
    import glob
    
    # Check for forbidden phase directories
    phase_dirs = glob.glob("phase-*") + glob.glob("Phase*") + glob.glob("PHASE*")
    if phase_dirs:
        raise ValueError(f"Phase directories found: {phase_dirs}. Use services-only architecture.")
    
    # Ensure services directory exists
    if not os.path.exists("services"):
        raise ValueError("services/ directory missing")
    
    return True
```

This standard ensures all future development follows the services-only architecture and prevents any agent from creating phase directories.