from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime

app = FastAPI(title="ATOM KMS Adapter", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class KeyRequest(BaseModel):
    key_id: str
    algorithm: str = "AES256"

@app.get("/health")
def health():
    return {"status": "healthy", "service": "kms-adapter", "simulation": SIMULATION_MODE}

@app.post("/keys/generate")
def generate_key(request: KeyRequest):
    """Generate encryption key"""
    if SIMULATION_MODE:
        return {
            "key_id": request.key_id,
            "algorithm": request.algorithm,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
    
    return {"error": "KMS unavailable"}

@app.post("/keys/{key_id}/encrypt")
def encrypt_data(key_id: str, data: dict):
    """Encrypt data with KMS key"""
    if SIMULATION_MODE:
        return {
            "ciphertext": f"encrypted_{hashlib.sha256(json.dumps(data).encode()).hexdigest()[:16]}",
            "key_id": key_id
        }
    
    return {"error": "KMS unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8304)