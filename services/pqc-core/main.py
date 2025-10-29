from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime
from prometheus_client import Counter, generate_latest

app = FastAPI(title="ATOM PQC Core", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
PQC_MODE = os.getenv("PQC_MODE", "hybrid")

# Metrics
pqc_operations_total = Counter("pqc_operations_total", "Total PQC operations", ["operation", "mode"])

class EncryptRequest(BaseModel):
    message: str
    algorithm: str = "kyber768"

class DecryptRequest(BaseModel):
    ciphertext: str
    private_key: str
    algorithm: str = "kyber768"

def enforce_p1_policy(operation: str):
    """P1: Data Privacy - no raw key material in logs"""
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "service": "pqc-core",
        "policy": "P1",
        "key_logged": False
    }
    print(f"AUDIT: {json.dumps(audit_entry)}")

def enforce_p2_policy(operation: str, key_id: str):
    """P2: Secrets & Signing - PQC keys stored securely"""
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "key_hash": hashlib.sha256(key_id.encode()).hexdigest()[:16],
        "service": "pqc-core",
        "policy": "P2"
    }
    print(f"AUDIT: {json.dumps(audit_entry)}")

@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "service": "pqc-core", 
        "simulation": SIMULATION_MODE,
        "pqc_mode": PQC_MODE
    }

@app.post("/pqc/encrypt")
def encrypt_message(request: EncryptRequest):
    """Encrypt message using PQC algorithms"""
    enforce_p1_policy("encrypt")
    pqc_operations_total.labels(operation="encrypt", mode=PQC_MODE).inc()
    
    if SIMULATION_MODE:
        # Simulate Kyber768 encryption
        mock_public_key = f"kyber_pub_{hashlib.sha256(request.message.encode()).hexdigest()[:16]}"
        mock_ciphertext = f"kyber_ct_{hashlib.sha256(request.message.encode()).hexdigest()}"
        
        enforce_p2_policy("keygen", mock_public_key)
        
        return {
            "ciphertext": mock_ciphertext,
            "public_key": mock_public_key,
            "algorithm": request.algorithm,
            "encrypted_at": datetime.now().isoformat(),
            "simulation": True
        }
    
    raise HTTPException(status_code=503, detail="PQC libraries unavailable")

@app.post("/pqc/decrypt")
def decrypt_message(request: DecryptRequest):
    """Decrypt message using PQC algorithms"""
    enforce_p1_policy("decrypt")
    pqc_operations_total.labels(operation="decrypt", mode=PQC_MODE).inc()
    
    if SIMULATION_MODE:
        # Simulate decryption - extract original from mock ciphertext
        if request.ciphertext.startswith("kyber_ct_"):
            return {
                "plaintext": "decrypted_message_simulation",
                "algorithm": request.algorithm,
                "decrypted_at": datetime.now().isoformat(),
                "simulation": True
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid ciphertext format")
    
    raise HTTPException(status_code=503, detail="PQC libraries unavailable")

@app.post("/pqc/keygen")
def generate_keypair(algorithm: str = "kyber768"):
    """Generate PQC keypair"""
    enforce_p1_policy("keygen")
    pqc_operations_total.labels(operation="keygen", mode=PQC_MODE).inc()
    
    if SIMULATION_MODE:
        key_id = hashlib.sha256(f"{algorithm}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        enforce_p2_policy("keygen", key_id)
        
        return {
            "key_id": key_id,
            "algorithm": algorithm,
            "public_key": f"{algorithm}_pub_{key_id}",
            "created_at": datetime.now().isoformat(),
            "quantum_safe": True,
            "simulation": True
        }
    
    raise HTTPException(status_code=503, detail="PQC libraries unavailable")

@app.get("/metrics")
def metrics():
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8601)