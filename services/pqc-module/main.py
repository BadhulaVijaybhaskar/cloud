from fastapi import FastAPI
from pydantic import BaseModel
import os
import hashlib
from datetime import datetime

app = FastAPI(title="ATOM PQC Module", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class PQCKeyRequest(BaseModel):
    algorithm: str = "kyber768"
    purpose: str = "encryption"

@app.get("/health")
def health():
    return {"status": "healthy", "service": "pqc-module", "simulation": SIMULATION_MODE}

@app.get("/pqc/mode")
def get_pqc_mode():
    """Get PQC operational mode"""
    return {"mode": "simulation" if SIMULATION_MODE else "production", "algorithms": ["kyber768", "dilithium3"]}

@app.post("/pqc/keygen")
def generate_pqc_keypair(request: PQCKeyRequest):
    """Generate post-quantum cryptography keypair"""
    if SIMULATION_MODE:
        key_id = hashlib.sha256(f"{request.algorithm}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        return {
            "key_id": key_id,
            "algorithm": request.algorithm,
            "public_key": f"pqc_pub_{key_id}",
            "created_at": datetime.now().isoformat(),
            "quantum_safe": True
        }
    
    return {"error": "PQC libraries unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8305)