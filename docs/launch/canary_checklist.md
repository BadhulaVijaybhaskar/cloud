# Canary Checklist

## Pre-Canary
- [ ] Snapshot DBs
- [ ] Confirm `SIMULATION_MODE=false` set only for canary namespace
- [ ] Confirm `APPROVE_DEPLOY=yes` present
- [ ] Notify stakeholders with time window

## Canary Run
- Deploy to `atom-canary` namespace
- Validate health endpoints for all primary services:
  - `/health` status==healthy
  - `/metrics` returns metrics
- Run synthetic traffic for 2 hours
- Validate billing events pipeline with sample events

## Observation
- Monitor 48 hours
- If no critical incidents, schedule staggered expansion