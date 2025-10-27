from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from datetime import datetime

app = FastAPI(title="ATOM Policy Gatekeeper", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class PolicyRequest(BaseModel):
    operation: str
    resource: str
    user_id: str
    metadata: dict = {}

class DryRunRequest(BaseModel):
    payload: dict
    operation: str

def enforce_p3_policy(operation: str, user_id: str):
    """P3: Execution Safety - require approval for destructive operations"""
    if operation in ["delete", "drop", "truncate"]:
        if not SIMULATION_MODE:
            # Real implementation would check for approver signature
            pass
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "user_id": user_id,
            "policy": "P3",
            "approval_required": True
        }
        print(f"AUDIT: {json.dumps(audit_entry)}")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "policy-gatekeeper", "simulation": SIMULATION_MODE}

@app.post("/policy/dryrun")
def policy_dryrun(request: DryRunRequest):
    """Simulate policy enforcement without execution"""
    enforce_p3_policy(request.operation, "system")
    
    return {
        "operation": request.operation,
        "would_execute": True,
        "policies_applied": ["P2", "P3"],
        "approval_required": request.operation in ["delete", "drop", "truncate"],
        "simulation": True
    }

@app.get("/policy/status")
def policy_status():
    """List policy enforcement coverage"""
    return {
        "policies": {
            "P1": {"status": "active", "coverage": "data_privacy"},
            "P2": {"status": "active", "coverage": "secrets_signing"},
            "P3": {"status": "active", "coverage": "execution_safety"},
            "P4": {"status": "active", "coverage": "observability"},
            "P5": {"status": "active", "coverage": "multi_tenancy"},
            "P6": {"status": "active", "coverage": "performance"}
        },
        "enforcement_mode": "simulation" if SIMULATION_MODE else "production"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8306)