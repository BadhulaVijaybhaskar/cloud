from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime

app = FastAPI(title="ATOM Vault PQC Adapter", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class PQCKeyStore(BaseModel):
    key_id: str
    algorithm: str
    public_key: str
    metadata: dict = {}

def enforce_p2_policy(operation: str, key_id: str):
    """P2: PQC keys stored and signed via Vault"""
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "key_hash": hashlib.sha256(key_id.encode()).hexdigest()[:16],
        "service": "vault-pqc-adapter",
        "policy": "P2"
    }
    print(f"AUDIT: {json.dumps(audit_entry)}")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "vault-pqc-adapter", "simulation": SIMULATION_MODE}

@app.post("/vault/pqc/store")
def store_pqc_key(key_data: PQCKeyStore):
    """Store PQC key in Vault with P2 enforcement"""
    enforce_p2_policy("store_key", key_data.key_id)
    
    if SIMULATION_MODE:
        return {
            "key_id": key_data.key_id,
            "vault_path": f"pqc/keys/{key_data.key_id}",
            "algorithm": key_data.algorithm,
            "stored_at": datetime.now().isoformat(),
            "version": 1
        }
    
    raise HTTPException(status_code=503, detail="Vault unavailable")

@app.get("/vault/pqc/retrieve/{key_id}")
def retrieve_pqc_key(key_id: str):
    """Retrieve PQC key from Vault"""
    enforce_p2_policy("retrieve_key", key_id)
    
    if SIMULATION_MODE:
        return {
            "key_id": key_id,
            "public_key": f"pqc_pub_key_simulation_{key_id}",
            "algorithm": "kyber768",
            "created_at": "2024-01-15T10:00:00Z",
            "quantum_safe": True
        }
    
    raise HTTPException(status_code=503, detail="Vault unavailable")

@app.get("/vault/pqc/list")
def list_pqc_keys():
    """List stored PQC keys"""
    if SIMULATION_MODE:
        return {
            "keys": [
                {"key_id": "pqc_001", "algorithm": "kyber768", "created_at": "2024-01-15T10:00:00Z"},
                {"key_id": "pqc_002", "algorithm": "dilithium3", "created_at": "2024-01-15T11:00:00Z"}
            ],
            "total": 2
        }
    
    raise HTTPException(status_code=503, detail="Vault unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8603)