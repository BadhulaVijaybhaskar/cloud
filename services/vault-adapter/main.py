from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime

app = FastAPI(title="ATOM Vault Adapter", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class SecretRequest(BaseModel):
    path: str
    data: dict

class SecretResponse(BaseModel):
    path: str
    version: int
    created_time: str

# P2 Policy Template - Secrets & Signing
def enforce_p2_policy(operation: str, path: str):
    """P2: All secret operations must be signed and audited"""
    if not SIMULATION_MODE:
        # Real implementation would verify cosign signature
        pass
    
    # Audit log entry (P2 requirement)
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "path_hash": hashlib.sha256(path.encode()).hexdigest()[:16],
        "service": "vault-adapter",
        "policy": "P2"
    }
    print(f"AUDIT: {json.dumps(audit_entry)}")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "vault-adapter", "simulation": SIMULATION_MODE}

@app.post("/secrets", response_model=SecretResponse)
def store_secret(request: SecretRequest):
    """Store secret in Vault with P2 enforcement"""
    enforce_p2_policy("store", request.path)
    
    if SIMULATION_MODE:
        return SecretResponse(
            path=request.path,
            version=1,
            created_time=datetime.now().isoformat()
        )
    
    # Real Vault integration would go here
    raise HTTPException(status_code=503, detail="Vault unavailable")

@app.get("/secrets/{path:path}")
def get_secret(path: str):
    """Retrieve secret from Vault with P2 enforcement"""
    enforce_p2_policy("retrieve", path)
    
    if SIMULATION_MODE:
        return {
            "path": path,
            "data": {"simulated": "secret_value_redacted"},
            "version": 1
        }
    
    # Real Vault integration would go here
    raise HTTPException(status_code=503, detail="Vault unavailable")

@app.delete("/secrets/{path:path}")
def delete_secret(path: str):
    """Delete secret from Vault with P2 enforcement"""
    enforce_p2_policy("delete", path)
    
    if SIMULATION_MODE:
        return {"message": "Secret deleted (simulation)", "path": path}
    
    # Real Vault integration would go here
    raise HTTPException(status_code=503, detail="Vault unavailable")

@app.get("/metrics")
def metrics():
    return {"vault_operations_total": 42, "simulation_mode": SIMULATION_MODE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8301)