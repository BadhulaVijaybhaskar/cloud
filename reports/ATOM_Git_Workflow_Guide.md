# ATOM Cloud Git Workflow Guide

**For Future Development & AI Agents**

## Current Repository State

- **Repository**: ATOM Cloud Platform (d:\Project\Suite\Cloud)
- **Current Branch**: `prod-feature/I.8-simulation-sandbox`
- **Total Branches**: 64 local branches
- **Phases Complete**: 30/35 (85.7%)
- **Services**: 80+ microservices in `services/` directory

## Established Branching Patterns

### 1. **Feature Branch Strategy** (Recommended for Major Features)
```bash
# Pattern: prod-feature/X.Y-descriptive-name
git checkout -b prod-feature/J.2-developer-console
git add .
git commit -m "feat(J.2): Developer Console implementation"
git push -u origin prod-feature/J.2-developer-console
```

**Use for:**
- New major UI components (J.2, J.3)
- Complex integrations
- Substantial new features
- Parallel development needs

### 2. **Direct Commits Strategy** (For Quick Updates)
```bash
# Stay on current branch
git add .
git commit -m "fix(I.9): Update governance test validation"
git push origin prod-feature/I.8-simulation-sandbox
```

**Use for:**
- Bug fixes
- Documentation updates
- Minor enhancements
- Quick iterations

### 3. **Hybrid Strategy** (Current Approach)
- **Major features**: Create dedicated branches
- **Minor work**: Direct commits to current branch
- **Completion work**: Use existing feature branches

## Commit Message Convention

```bash
# Format: type(scope): description
feat(J.2): Add developer console dashboard
fix(I.9): Resolve governance test timeout
docs(README): Update installation instructions
refactor(services): Optimize metrics collection
test(I.8): Add simulation scenario validation
```

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Branch Naming Convention

```bash
# Feature branches
prod-feature/X.Y-component-name
prod-feature/J.2-developer-console
prod-feature/J.3-marketplace-ui

# Review branches  
prod-review/PhaseX-Finalization
prod-review/PhaseJ-Finalization

# Hardening branches
prod-hardening/NN-feature-name
prod-hardening/08-performance-optimization

# Special branches
feat/description
main
```

## Current Work Status & Next Steps

### ✅ **Complete Phases (30/35) - MAINTAIN ONLY**
- A.1-A.3, B.1-B.6, C.1-C.5, D.1-D.4, E.1-E.5, F.1-F.3, G.1-G.4, H.4-H.5, I.1-I.9, J.1
- **Action**: Bug fixes only via direct commits

### ⚠️ **Partial Phases (3/35) - COMPLETE ON EXISTING BRANCHES**
```bash
# H.1 - Complete LangGraph Integration
git checkout prod-feature/H.1.1-pqc-core
# Complete workflow implementation

# H.2 - Complete API Layer
git checkout prod-feature/H.2.1-neural-fabric-scheduler  
# Add advanced proxy features

# H.3 - Complete Workflow Integration
git checkout prod-feature/H.3.1-hybrid-coordinator
# Add realtime bridge implementation
```

### ❌ **Pending Phases (2/35) - CREATE NEW BRANCHES**
```bash
# J.2 - Developer Console (LaunchPad)
git checkout -b prod-feature/J.2-developer-console
# Implement React/Next.js developer dashboard

# J.3 - Marketplace UI  
git checkout -b prod-feature/J.3-marketplace-ui
# Implement model browsing and purchase flows
```

## File Organization Patterns

### **Phase Directories** (Recent phases only)
```
phase-i5/    # Collective Intelligence Network
phase-i6/    # Adaptive Optimization Layer  
phase-i7/    # Advanced Optimization Control
phase-i8/    # Global Simulation Sandbox
phase-i9/    # Governance Testing Framework
phase-j1/    # Production Launch Operations
```

### **Services Directory** (All microservices)
```
services/
├── auth/                    # Authentication
├── aol-*/                   # AOL services (I.7)
├── global-*/                # I.1 services
├── context-*/               # I.3 services
├── decision-*/              # I.4 services
└── [80+ other services]
```

### **Infrastructure**
```
infra/
├── terraform/               # Infrastructure as code
├── helm/                    # Kubernetes deployments
├── monitoring/              # Prometheus, Grafana
└── sql/                     # Database schemas
```

## Push & Merge Strategy

### **For New Features (J.2, J.3)**
```bash
# 1. Create feature branch
git checkout -b prod-feature/J.2-developer-console

# 2. Implement feature
# ... development work ...

# 3. Commit with proper messages
git add .
git commit -m "feat(J.2): Add developer console dashboard"

# 4. Push to remote
git push -u origin prod-feature/J.2-developer-console

# 5. Create PR (when ready)
# 6. Merge to main after review
```

### **For Bug Fixes & Updates**
```bash
# Stay on current branch (I.8)
git add .
git commit -m "fix(I.9): Resolve test validation issue"
git push origin prod-feature/I.8-simulation-sandbox
```

### **For Completing Partial Work**
```bash
# Use existing feature branch
git checkout prod-feature/H.1.1-pqc-core
git add .
git commit -m "feat(H.1): Complete LangGraph workflow engine"
git push origin prod-feature/H.1.1-pqc-core
```

## Repository Access Points

### **All Phases Available From:**
- `prod-feature/I.8-simulation-sandbox` (current) - Contains I.1-I.9, J.1
- `main` - Contains A-I.4 phases
- Individual feature branches - For specific phase work

### **Missing Separate Branches:**
- I.1-I.6, I.9 (committed directly, no separate branches)
- J.2-J.3 (not yet implemented)

## Quality Guidelines

### **Before Pushing:**
1. **Test locally**: Ensure services start and basic functionality works
2. **Check dependencies**: Verify all imports and requirements are met
3. **Update documentation**: Add/update README files for new features
4. **Follow naming**: Use established patterns for files and directories
5. **Commit atomically**: One logical change per commit

### **Commit Standards:**
- **Descriptive messages**: Explain what and why, not just what
- **Proper scope**: Use phase/component identifiers (I.9, J.2, etc.)
- **Breaking changes**: Mark with `BREAKING CHANGE:` in commit body
- **Issue references**: Link to issues when applicable

## Emergency Procedures

### **If Branch is Corrupted:**
```bash
# Reset to last known good commit
git reset --hard <commit-hash>

# Or restore from remote
git fetch origin
git reset --hard origin/prod-feature/I.8-simulation-sandbox
```

### **If Files are Missing:**
```bash
# Check git history for files
git log --follow -- path/to/file

# Restore from specific commit
git checkout <commit-hash> -- path/to/file
```

### **If Need to Switch Context:**
```bash
# Save current work
git stash

# Switch branch
git checkout target-branch

# Resume work later
git stash pop
```

## Future Development Recommendations

1. **Continue Hybrid Strategy**: Feature branches for major work, direct commits for minor
2. **Complete H-Series**: Finish H.1-H.3 on existing branches before new work
3. **Implement J-Series**: Create dedicated branches for J.2-J.3 UI work
4. **Maintain Documentation**: Keep phase matrix and reports updated
5. **Preserve History**: Don't rewrite history, maintain commit lineage

---

**This guide ensures consistent development patterns and helps future AI agents understand the established workflow for the ATOM Cloud Platform.**