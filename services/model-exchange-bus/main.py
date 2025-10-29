#!/usr/bin/env python3
import os
import json
import logging
import hashlib
from fastapi import FastAPI, UploadFile, File
from typing import Dict, Any

app = FastAPI(title="Model Exchange Bus")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

# In-memory storage for simulation
model_store = {}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "model-exchange-bus", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {
        "models_uploaded": len(model_store),
        "downloads_total": sum(m.get("download_count", 0) for m in model_store.values()),
        "storage_mb": sum(m.get("size_mb", 0) for m in model_store.values()),
        "simulation": SIMULATION_MODE
    }

@app.post("/models/upload")
async def upload_model(
    file: UploadFile = File(...),
    metadata: str = None
):
    if SIMULATION_MODE:
        # Simulate model upload and verification
        model_id = f"model-{hash(file.filename) % 10000}"
        
        # Simulate reading file content for hash
        content_hash = hashlib.sha256(file.filename.encode()).hexdigest()[:16]
        
        model_metadata = json.loads(metadata) if metadata else {}
        
        model_record = {
            "model_id": model_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size_mb": 45.7,  # Simulated size
            "content_hash": content_hash,
            "cosign_signature": "<REDACTED>",  # P2 compliance
            "signature_verified": True,
            "uploaded_at": "2024-01-15T10:30:00Z",
            "metadata": model_metadata,
            "download_count": 0,
            "audit_hash": f"sha256:{hash(model_id) % 100000}",
            "simulation": True
        }
        
        model_store[model_id] = model_record
        
        logger.info(f"Model uploaded: {model_id} ({file.filename})")
        return {
            "status": "uploaded",
            "model_id": model_id,
            "content_hash": content_hash,
            "signature_verified": True,
            "simulation": True
        }
    
    return {"status": "error", "message": "Model storage infrastructure required"}

@app.get("/models/{model_id}/download")
async def download_model(model_id: str):
    if SIMULATION_MODE:
        if model_id in model_store:
            model = model_store[model_id]
            model["download_count"] = model.get("download_count", 0) + 1
            
            return {
                "model_id": model_id,
                "download_url": f"https://models.atom.cloud/{model_id}",
                "content_hash": model["content_hash"],
                "signature": model["cosign_signature"],
                "expires_at": "2024-01-15T11:30:00Z",
                "simulation": True
            }
        
        return {"status": "not_found", "model_id": model_id}
    
    return {"status": "error", "message": "Model storage required"}

@app.get("/models/{model_id}/info")
async def get_model_info(model_id: str):
    if SIMULATION_MODE:
        if model_id in model_store:
            model = model_store[model_id].copy()
            # Remove sensitive data
            model.pop("cosign_signature", None)
            return model
        
        return {"status": "not_found", "model_id": model_id}
    
    return {"status": "error", "message": "Model metadata required"}

@app.get("/models/catalog")
async def list_models():
    if SIMULATION_MODE:
        catalog = []
        for model_id, model in model_store.items():
            catalog.append({
                "model_id": model_id,
                "filename": model["filename"],
                "size_mb": model["size_mb"],
                "uploaded_at": model["uploaded_at"],
                "download_count": model.get("download_count", 0)
            })
        
        return {
            "models": catalog,
            "total": len(catalog),
            "simulation": True
        }
    
    return {"status": "error", "message": "Model catalog required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9003)