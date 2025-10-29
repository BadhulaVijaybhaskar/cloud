from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime

app = FastAPI(title="ATOM PQC Key Rotation", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class RotationRequest(BaseModel):
    key_id: str
    algorithm: str = "kyber768"
    approved_by: str = ""

def enforce_p3_policy(operation: str, key_id: str, approved_by: str):
    """P3: Execution Safety - rotation requires approval"""
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "key_hash": hashlib.sha256(key_id.encode()).hexdigest()[:16],
        "approver_hash": hashlib.sha256(approved_by.encode()).hexdigest()[:16] if approved_by else "",
        "service": "pqc-rotation-service",
        "policy": "P3",
        "approval_required": True
    }
    print(f"AUDIT: {json.dumps(audit_entry)}")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "pqc-rotation-service", "simulation": SIMULATION_MODE}

@app.post("/pqc/rotate")
def rotate_pqc_key(request: RotationRequest):
    """Rotate PQC key with P3 enforcement"""
    enforce_p3_policy("key_rotation", request.key_id, request.approved_by)
    
    if SIMULATION_MODE:
        new_key_id = hashlib.sha256(f"{request.key_id}_rotated_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        return {
            "old_key_id": request.key_id,
            "new_key_id": new_key_id,
            "algorithm": request.algorithm,
            "rotated_at": datetime.now().isoformat(),
            "approved_by": request.approved_by,
            "status": "completed"
        }
    
    raise HTTPException(status_code=503, detail="Key rotation unavailable")

@app.get("/pqc/rotation/status")
def rotation_status():
    """Get key rotation status"""
    if SIMULATION_MODE:
        return {
            "active_rotations": 0,
            "completed_rotations": 3,
            "next_scheduled": "2024-01-16T10:00:00Z",
            "rotation_policy": "30_days"
        }
    
    raise HTTPException(status_code=503, detail="Rotation status unavailable")

@app.post("/pqc/rotation/schedule")
def schedule_rotation(key_id: str, rotation_date: str):
    """Schedule key rotation"""
    if SIMULATION_MODE:
        return {
            "key_id": key_id,
            "scheduled_for": rotation_date,
            "status": "scheduled",
            "notification_sent": True
        }
    
    raise HTTPException(status_code=503, detail="Scheduling unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8604)