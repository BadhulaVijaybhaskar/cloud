# Phase Directory Reference Guide

**TEMPORARY LOCAL DOCUMENT - NOT FOR GIT**

## Quick Reference for Migration Work

### Phase Directory Locations
```
d:\Project\Suite\Cloud\phase-i5\    # Collective Intelligence Network
d:\Project\Suite\Cloud\phase-i6\    # Adaptive Optimization Layer
d:\Project\Suite\Cloud\phase-i7\    # Advanced Optimization Control
d:\Project\Suite\Cloud\phase-i8\    # Global Simulation Sandbox
d:\Project\Suite\Cloud\phase-i9\    # Governance Testing Framework
d:\Project\Suite\Cloud\phase-j1\    # Production Launch Operations
```

### Critical Files with Phase References

#### High Impact (Active Code)
```
services/policy-engine/main.py
- Line references to phase-i5 paths
- Needs immediate update during migration

phase-i5/scripts/deploy.sh
- Infrastructure deployment scripts
- Update terraform paths

phase-i6/services/adaptive-optimization-engine/config.yaml
- Service configuration with hardcoded paths
- Update service discovery endpoints

phase-i8/infra/terraform/main.tf
- Infrastructure as code
- Update resource references
```

#### Medium Impact (Configuration)
```
phase-i5/tests/integration/test_collective_intelligence.py
phase-i6/tests/unit/test_adaptive_optimization.py
phase-i8/tests/e2e/test_simulation_scenarios.py
- Test files with relative path imports
- Update import statements

phase-i5/contracts/CollectiveIntelligence.sol
phase-i6/contracts/AdaptiveOptimization.sol
- Smart contracts with deployment configs
- Update deployment scripts
```

#### Low Impact (Documentation)
```
phase-i7/README.md
phase-i9/README.md
phase-j1/README.md
- Documentation with internal links
- Update after migration for consistency
```

### Complete Migration Mapping

#### Services → services/
```
phase-i5/services/* → services/collective-intelligence-*
phase-i6/services/* → services/adaptive-optimization-*
phase-i8/services/* → services/simulation-*
```

#### Infrastructure → infra/
```
phase-i5/infra/terraform/* → infra/terraform/modules/collective-intelligence/
phase-i6/infra/terraform/* → infra/terraform/modules/adaptive-optimization/
phase-i5/infra/helm/* → infra/helm/collective-intelligence/
phase-i6/infra/helm/* → infra/helm/adaptive-optimization/
phase-i7/infra/helm/* → infra/helm/advanced-optimization/
phase-i8/infra/helm/* → infra/helm/simulation/
phase-j1/infra/kubernetes/* → infra/helm/production-launch/
```

#### Tests → tests/
```
phase-i5/tests/* → tests/collective-intelligence/
phase-i6/tests/* → tests/adaptive-optimization/
phase-i8/tests/* → tests/simulation/
```

#### Scripts → infra/scripts/
```
phase-i*/scripts/* → infra/scripts/[service-name]/
phase-j*/scripts/* → infra/scripts/[service-name]/
```

#### Contracts → infra/contracts/ (NEW)
```
phase-i5/contracts/* → infra/contracts/collective-intelligence/
phase-i6/contracts/* → infra/contracts/adaptive-optimization/
```

#### Security → infra/security/ (NEW)
```
phase-i*/security/* → infra/security/[service-name]/
```

#### Policies → infra/vault/policies/
```
phase-i*/policies/* → infra/vault/policies/[service-name].hcl
```

### New Directory Creation Required

#### Create These Directories
```bash
mkdir infra\contracts
mkdir infra\security
```

#### Target Global Structure (Matches Existing Pattern)
```
Cloud/
├── services/                    # All microservices
├── infra/
│   ├── terraform/modules/       # Service-specific terraform modules
│   ├── helm/                    # Service-specific helm charts
│   ├── contracts/               # Smart contracts by service (NEW)
│   ├── security/                # Security configs by service (NEW)
│   ├── scripts/                 # Service-specific scripts
│   └── vault/policies/          # Service-specific policies (.hcl files)
└── tests/                       # Service-specific tests
```

### Search Commands for Reference

#### Find Phase References
```bash
# Python files
findstr /s /i "phase-i" *.py

# YAML/JSON configs
findstr /s /i "phase-i" *.yaml *.yml *.json

# Documentation
findstr /s /i "phase-i" *.md *.rst *.txt

# All files
findstr /s /i "phase-i" *.*
```

#### Find Import Statements
```bash
# Python imports
findstr /s "from phase-" *.py
findstr /s "import.*phase-" *.py

# Relative imports
findstr /s "\.\./phase-" *.*
findstr /s "\.\.\.phase-" *.*
```

### Migration Checklist

#### Pre-Migration
- [ ] Backup current branch state
- [ ] Document all phase directory contents
- [ ] Map all file references
- [ ] Test current functionality

#### During Migration
- [ ] Move services to `services/` directory
- [ ] Update import statements in Python files
- [ ] Update configuration file paths
- [ ] Move infrastructure to `infra/phases/`
- [ ] Update documentation links

#### Post-Migration
- [ ] Test all service imports
- [ ] Verify infrastructure deployments
- [ ] Run integration tests
- [ ] Update documentation
- [ ] Remove empty phase directories

### Backup Strategy
```bash
# Create backup branch before migration
git checkout -b backup/pre-phase-migration
git add .
git commit -m "backup: Pre-phase directory migration state"

# Work on migration branch
git checkout -b feature/phase-directory-migration
```

### Validation Commands
```bash
# Test Python imports
python -c "import services.collective_intelligence_core"

# Check service discovery
docker-compose ps | grep collective-intelligence

# Verify infrastructure
terraform plan -chdir="infra/terraform/modules/collective-intelligence"
```

---

## ✅ MIGRATION STATUS: COMPONENTS COMPLETE

**Date Updated**: December 2024
**Status**: ALL COMPONENTS MIGRATED
**Remaining**: Path references in reports and workflows only

### ✅ Path References Updated:

#### Reports (COMPLETED)
```
reports/PhaseI.5_Final_Snapshot.json
✅ Updated all phase-i5 paths to global directory structure
- contracts: phase-i5/contracts/* → infra/contracts/collective-intelligence/*
- security: phase-i5/security/* → infra/security/collective-intelligence/*
- policies: phase-i5/policies/* → infra/vault/policies/collective-intelligence.hcl
- privacy: phase-i5/privacy/* → docs/privacy/collective-intelligence/*
- monitoring: phase-i5/observability/* → infra/monitoring/collective-intelligence/*
- build: phase-i5/Makefile → infra/scripts/collective-intelligence/Makefile
- tests: phase-i5/tests/* → tests/collective-intelligence/*
- scripts: phase-i5/prechecks/* → infra/scripts/collective-intelligence/*
- cli: phase-i5/cli/* → infra/scripts/collective-intelligence/*

reports/PhaseI.5_Snapshot.json
✅ Updated all phase-i5 path references to new global structure
```

#### Backup Files (COMPLETED)
```
backups/phase-directories/phase-i5/manifests/helm/signal-gateway/Chart.yaml
✅ Updated GitHub URL: phase-i5 → infra/helm/collective-intelligence

backups/phase-directories/phase-i6/policies/policy-matrix.yaml
✅ Updated path comment: phase-i6 → infra/vault/policies/adaptive-optimization.hcl
```

#### GitHub Workflows (PRESERVED)
```
.github/workflows/project-auto-sync.yml
ℹ️ Phase labels preserved for backward compatibility
ℹ️ Component labels can be added in future if needed
```

### ✅ COMPONENT MIGRATION COMPLETED

**All Missing Components Successfully Migrated:**
- **Phase I.5**: ✅ 8 components (CLI, Helm, Observability, Prechecks, Privacy, UI, Build, Docs)
- **Phase I.6**: ✅ 1 component (Scripts)
- **Phase I.8**: ✅ 3 components (Scenarios, Docs, Dependencies)
- **Phase I.9**: ✅ 3 components (Connectors, Infra Checks, Docs)
- **Phase J.1**: ✅ 1 component (Docs)

**TOTAL MIGRATED**: ✅ 16 components + original migration

**✅ ALL ISSUES RESOLVED**: Path references updated successfully

---
**Purpose**: Document completed migration
**Usage**: Reference for future development
**Status**: MIGRATION FULLY COMPLETE - All components migrated and path references updated