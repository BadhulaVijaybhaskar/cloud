#!/usr/bin/env python3
"""
ATOM Model Registry - Port 8101
Model metadata and version management per J.3 spec
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
from typing import List, Optional

app = FastAPI(title="ATOM Model Registry", version="1.0.0")

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

# Simulated database
models_db = {}
versions_db = {}

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "service": "model-registry",
        "port": 8101,
        "simulation_mode": SIMULATION_MODE
    }

@app.get("/v1/models")
async def list_models(tags: Optional[str] = None, vendor: Optional[str] = None, limit: int = 20):
    """List models with filters"""
    
    models = list(models_db.values())
    
    if vendor:
        models = [m for m in models if m.get("vendor_id") == vendor]
    
    if tags:
        tag_list = tags.split(",")
        models = [m for m in models if any(tag in m.get("tags", []) for tag in tag_list)]
    
    return {
        "models": models[:limit],
        "total": len(models),
        "simulation_mode": SIMULATION_MODE
    }

@app.get("/v1/models/{model_id}")
async def get_model(model_id: str):
    """Get model metadata and versions"""
    
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model = models_db[model_id]
    
    # Get all versions for this model
    model_versions = [v for v in versions_db.values() if v["model_id"] == model_id]
    model_versions.sort(key=lambda x: x["published_at"], reverse=True)
    
    return {
        **model,
        "versions": model_versions,
        "version_count": len(model_versions)
    }

@app.get("/v1/models/{model_id}/download")
async def download_model(model_id: str, version: Optional[str] = None):
    """Get signed download URL"""
    
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Find version
    if version:
        version_obj = next((v for v in versions_db.values() 
                          if v["model_id"] == model_id and v["version"] == version), None)
    else:
        # Get latest version
        model_versions = [v for v in versions_db.values() if v["model_id"] == model_id]
        version_obj = max(model_versions, key=lambda x: x["published_at"]) if model_versions else None
    
    if not version_obj:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Generate signed URL (simulated)
    signed_url = f"https://storage.atom.cloud/signed/{model_id}/{version_obj['version']}?token=sim_token"
    
    return {
        "download_url": signed_url,
        "model_id": model_id,
        "version": version_obj["version"],
        "size_mb": version_obj["size_mb"],
        "checksum": version_obj["checksum"],
        "expires_in": 3600,
        "simulation_mode": SIMULATION_MODE
    }

@app.post("/v1/models/{model_id}/retire")
async def retire_model(model_id: str):
    """Retire a model"""
    
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    models_db[model_id]["status"] = "retired"
    models_db[model_id]["retired_at"] = datetime.utcnow().isoformat()
    
    return {
        "model_id": model_id,
        "status": "retired",
        "message": "Model retired successfully"
    }

# Internal API for marketplace-core to register models
@app.post("/internal/register")
async def register_model(model_data: dict):
    """Internal API to register model from marketplace-core"""
    
    model_id = str(uuid.uuid4())
    
    # Create model entry
    model = {
        "id": model_id,
        "vendor_id": model_data["vendor_id"],
        "name": model_data["name"],
        "description": model_data["description"],
        "license": model_data["license"],
        "tags": model_data.get("tags", []),
        "created_at": datetime.utcnow().isoformat(),
        "status": "active",
        "latest_version": model_data["version"]
    }
    
    models_db[model_id] = model
    
    # Create version entry
    version_id = str(uuid.uuid4())
    version = {
        "id": version_id,
        "model_id": model_id,
        "version": model_data["version"],
        "artifact_path": model_data.get("artifact_url"),
        "checksum": model_data.get("checksum", "sim_checksum"),
        "size_mb": model_data.get("size_mb", 100),
        "metadata": model_data.get("safety_metadata", {}),
        "published_at": datetime.utcnow().isoformat(),
        "governance_status": "approved"
    }
    
    versions_db[version_id] = version
    
    return {
        "model_id": model_id,
        "version_id": version_id,
        "status": "registered"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8101)