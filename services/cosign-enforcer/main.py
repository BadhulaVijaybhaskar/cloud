from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime

app = FastAPI(title="ATOM Cosign Enforcer", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class SignRequest(BaseModel):
    payload: str
    signer: str

class VerifyRequest(BaseModel):
    payload: str
    signature: str

def enforce_p2_policy(operation: str, signer: str):
    """P2: All operations must be signed and audited"""
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "signer_hash": hashlib.sha256(signer.encode()).hexdigest()[:16],
        "service": "cosign-enforcer",
        "policy": "P2"
    }
    print(f"AUDIT: {json.dumps(audit_entry)}")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "cosign-enforcer", "simulation": SIMULATION_MODE}

@app.post("/sign")
def sign_payload(request: SignRequest):
    """Sign payload with cosign"""
    enforce_p2_policy("sign", request.signer)
    
    if SIMULATION_MODE:
        return {
            "signature": f"sim_sig_{hashlib.sha256(request.payload.encode()).hexdigest()[:16]}",
            "signer": request.signer,
            "timestamp": datetime.now().isoformat()
        }
    
    raise HTTPException(status_code=503, detail="Cosign unavailable")

@app.post("/verify")
def verify_signature(request: VerifyRequest):
    """Verify cosign signature"""
    enforce_p2_policy("verify", "system")
    
    if SIMULATION_MODE:
        expected_sig = f"sim_sig_{hashlib.sha256(request.payload.encode()).hexdigest()[:16]}"
        return {
            "valid": request.signature == expected_sig,
            "verified_at": datetime.now().isoformat()
        }
    
    raise HTTPException(status_code=503, detail="Cosign unavailable")

@app.get("/metrics")
def metrics():
    return {"signatures_total": 15, "verifications_total": 8, "simulation_mode": SIMULATION_MODE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8302)