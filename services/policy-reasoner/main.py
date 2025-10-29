#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Policy Reasoner")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class ProposalRequest(BaseModel):
    tenant_id: str
    context_id: str
    risk_id: str
    risk_score: float = 0.5

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "policy-reasoner", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {"proposals_generated": 89, "policies_applied": 67, "simulation": SIMULATION_MODE}

@app.post("/propose")
async def generate_proposals(req: ProposalRequest):
    if SIMULATION_MODE:
        # Simulate AI-driven policy reasoning
        proposals = []
        
        if req.risk_score > 0.7:
            proposals.extend([
                {"action": "scale_up", "target": "compute", "params": {"replicas": 3}},
                {"action": "enable_rate_limiting", "target": "api", "params": {"limit": 100}}
            ])
        elif req.risk_score > 0.4:
            proposals.append(
                {"action": "monitor_closely", "target": "metrics", "params": {"interval": "1m"}}
            )
        
        result = {
            "tenant_id": req.tenant_id,
            "proposals": proposals,
            "reasoning": f"Risk score {req.risk_score} requires {'immediate' if req.risk_score > 0.7 else 'standard'} action",
            "confidence": 0.85,
            "requires_approval": req.risk_score > 0.6,
            "simulation": True
        }
        
        logger.info(f"Generated {len(proposals)} proposals for {req.tenant_id}")
        return result
    
    return {"status": "error", "message": "AI reasoning engine required"}

@app.get("/policies/{tenant_id}")
async def get_active_policies(tenant_id: str):
    if SIMULATION_MODE:
        return {
            "tenant_id": tenant_id,
            "active_policies": [
                {"id": "pol-1", "type": "auto_scale", "status": "active"},
                {"id": "pol-2", "type": "cost_limit", "status": "active"}
            ],
            "simulation": True
        }
    
    return {"status": "error", "message": "Policy storage required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8803)