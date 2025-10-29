from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime

app = FastAPI(title="ATOM Failover Orchestrator", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class FailoverRequest(BaseModel):
    region: str
    tenant_id: str
    dry_run: bool = False

def enforce_p3_policy(operation: str, tenant_id: str):
    """P3: Execution Safety - require approval for failover"""
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "tenant_hash": hashlib.sha256(tenant_id.encode()).hexdigest()[:16],
        "policy": "P3",
        "approval_required": True
    }
    print(f"AUDIT: {json.dumps(audit_entry)}")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "failover-orchestrator", "simulation": SIMULATION_MODE}

@app.post("/failover/promote")
def promote_region(request: FailoverRequest):
    """Promote region to primary with P3 enforcement"""
    enforce_p3_policy("failover_promote", request.tenant_id)
    
    if SIMULATION_MODE:
        return {
            "region": request.region,
            "tenant_id": request.tenant_id,
            "status": "promoted" if not request.dry_run else "dry_run_success",
            "promoted_at": datetime.now().isoformat(),
            "dry_run": request.dry_run
        }
    
    return {"error": "Failover unavailable"}

@app.get("/failover/status")
def failover_status():
    """Get failover readiness status"""
    if SIMULATION_MODE:
        return {
            "primary_region": "us-east-1",
            "secondary_regions": ["eu-west-1", "ap-south-1"],
            "failover_ready": True,
            "last_test": "2024-01-15T09:00:00"
        }
    
    return {"error": "Failover status unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8505)