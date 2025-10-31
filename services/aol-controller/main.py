#!/usr/bin/env python3
"""
AOL Controller - Adaptive Optimization Layer Core Service
Phase I.6.1 - Optimizer Core Implementation
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Import local modules
from optimizer import OptimizationEngine
from evaluator import BacktestEvaluator
from canary_runner import CanaryRunner
from explainability import ExplainabilityEngine
from audit_helper import AuditHelper

# Metrics
proposal_counter = Counter('aol_proposals_total', 'Total optimization proposals')
simulation_duration = Histogram('aol_simulation_duration_seconds', 'Simulation execution time')
apply_counter = Counter('aol_applies_total', 'Total optimization applications', ['status'])

# Models
class OptimizationRequest(BaseModel):
    scope: str
    changes: List[Dict]
    reason: str
    risk_level: str = "low"

class SimulationRequest(BaseModel):
    dry_run: bool = True

class ApplyRequest(BaseModel):
    dry_run: bool = False
    approver: Optional[str] = None

# Global state (in production would use database)
proposals_db = {}
simulation_mode = os.getenv("SIMULATION_MODE", "true").lower() == "true"

app = FastAPI(title="AOL Controller", version="1.0.0")

# Initialize engines
optimizer = OptimizationEngine(simulation_mode=simulation_mode)
evaluator = BacktestEvaluator(simulation_mode=simulation_mode)
canary_runner = CanaryRunner(simulation_mode=simulation_mode)
explainer = ExplainabilityEngine(simulation_mode=simulation_mode)
auditor = AuditHelper(simulation_mode=simulation_mode)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "aol-controller",
        "simulation_mode": simulation_mode,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.post("/v1/propose")
async def propose_optimization(request: OptimizationRequest):
    """Submit optimization proposal"""
    proposal_counter.inc()
    
    proposal_id = str(uuid.uuid4())
    
    # P1 Privacy: Check for PII in changes
    if any("pii" in str(change).lower() or "personal" in str(change).lower() for change in request.changes):
        raise HTTPException(status_code=400, detail="PII detected in optimization request")
    
    # P3 Execution Safety: Validate risk level
    if request.risk_level not in ["low", "medium", "high"]:
        request.risk_level = "medium"
    
    # P5 Multi-tenancy: Validate scope format
    if not request.scope.startswith(("tenant:", "org:", "global:")):
        raise HTTPException(status_code=400, detail="Invalid scope format")
    
    # Create proposal
    proposal = {
        "id": proposal_id,
        "scope": request.scope,
        "changes": request.changes,
        "reason": request.reason,
        "risk_level": request.risk_level,
        "status": "proposed",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "created_by": "aol-system",
        "pre_state_hash": None,
        "post_state_hash": None,
        "approver": None,
        "audit_ref": None
    }
    
    # P7 Resilience: Take pre-state snapshot
    if not simulation_mode:
        proposal["pre_state_hash"] = auditor.take_snapshot(f"pre_{proposal_id}")
    else:
        proposal["pre_state_hash"] = f"sim_hash_{int(time.time())}"
    
    proposals_db[proposal_id] = proposal
    
    return {
        "proposal_id": proposal_id,
        "status": "proposed",
        "risk_level": request.risk_level,
        "simulation_mode": simulation_mode
    }

@app.get("/v1/proposals/{proposal_id}")
async def get_proposal(proposal_id: str):
    """Get proposal status and explanation"""
    if proposal_id not in proposals_db:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    proposal = proposals_db[proposal_id]
    
    # Generate explanation
    explanation = explainer.explain_proposal(proposal)
    
    return {
        **proposal,
        "explanation": explanation
    }

@app.post("/v1/proposals/{proposal_id}/simulate")
async def simulate_proposal(proposal_id: str, request: SimulationRequest):
    """Run simulation/canary for proposal"""
    if proposal_id not in proposals_db:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    proposal = proposals_db[proposal_id]
    
    with simulation_duration.time():
        # Run backtest evaluation
        backtest_result = evaluator.evaluate_proposal(proposal)
        
        # Generate canary plan
        canary_plan = canary_runner.generate_canary_plan(proposal)
        
        # P6 Performance: Check if simulation meets SLO
        if backtest_result.get("p95_latency_ms", 0) > 1000:
            proposal["status"] = "rejected"
            proposal["rejection_reason"] = "P6 violation: exceeds latency SLO"
        else:
            proposal["status"] = "simulated"
    
    proposals_db[proposal_id] = proposal
    
    return {
        "proposal_id": proposal_id,
        "status": proposal["status"],
        "backtest_result": backtest_result,
        "canary_plan": canary_plan,
        "simulation_mode": simulation_mode
    }

@app.post("/v1/proposals/{proposal_id}/apply")
async def apply_proposal(proposal_id: str, request: ApplyRequest):
    """Apply optimization proposal"""
    if proposal_id not in proposals_db:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    proposal = proposals_db[proposal_id]
    
    # P3 Execution Safety: Check approval requirements
    if proposal["risk_level"] in ["medium", "high"] and not request.approver and not request.dry_run:
        if not simulation_mode:
            raise HTTPException(status_code=403, detail="High-risk changes require approver")
    
    if request.dry_run:
        # Dry run mode
        result = {
            "proposal_id": proposal_id,
            "status": "dry_run_success",
            "changes_applied": len(proposal["changes"]),
            "rollback_plan": canary_runner.generate_rollback_plan(proposal),
            "simulation_mode": simulation_mode
        }
        apply_counter.labels(status="dry_run").inc()
    else:
        # Actual apply
        try:
            # P7 Resilience: Execute with rollback capability
            apply_result = optimizer.apply_changes(proposal["changes"], proposal["scope"])
            
            # P2 Signing: Record in audit log
            audit_ref = auditor.record_change(proposal, request.approver)
            
            proposal["status"] = "applied"
            proposal["approver"] = request.approver
            proposal["audit_ref"] = audit_ref
            proposal["post_state_hash"] = auditor.take_snapshot(f"post_{proposal_id}")
            
            result = {
                "proposal_id": proposal_id,
                "status": "applied",
                "audit_ref": audit_ref,
                "simulation_mode": simulation_mode
            }
            apply_counter.labels(status="success").inc()
            
        except Exception as e:
            proposal["status"] = "failed"
            apply_counter.labels(status="error").inc()
            raise HTTPException(status_code=500, detail=f"Apply failed: {str(e)}")
    
    proposals_db[proposal_id] = proposal
    return result

if __name__ == "__main__":
    port = int(os.getenv("AOL_PORT", "8601"))
    uvicorn.run(app, host="0.0.0.0", port=port)