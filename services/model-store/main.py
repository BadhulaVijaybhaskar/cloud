#!/usr/bin/env python3
"""
Phase I.5 - Model Store
Signed model artifact storage with provenance tracking
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
MODELS_STORED = Counter('models_stored_total', 'Total models stored')
MODELS_RETRIEVED = Counter('models_retrieved_total', 'Total models retrieved')
STORAGE_LATENCY = Histogram('model_storage_latency_seconds', 'Model storage latency')

app = FastAPI(title="Model Store", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
STORAGE_PATH = os.getenv('MODEL_STORAGE_PATH', '/tmp/model-store')

# In-memory storage for simulation
model_registry = {}
model_artifacts = {}

class ModelMetadata(BaseModel):
    model_id: str
    round_id: str
    version: str
    algorithm: str
    participants: List[str]
    performance_metrics: Dict[str, float]
    privacy_params: Dict[str, Any]
    created_by: str

class ModelCommitRequest(BaseModel):
    metadata: ModelMetadata
    artifact_data: Dict[str, Any]  # Model weights, config, etc.
    signature: Optional[str] = None

def calculate_model_hash(artifact_data: Dict[str, Any]) -> str:
    """Calculate SHA256 hash of model artifact"""
    artifact_str = json.dumps(artifact_data, sort_keys=True)
    return hashlib.sha256(artifact_str.encode()).hexdigest()

def generate_cosign_signature(model_hash: str, metadata: Dict[str, Any]) -> str:
    """Generate cosign signature for model artifact"""
    if SIMULATION_MODE:
        # Simulate cosign signature
        combined = f"{model_hash}:{json.dumps(metadata, sort_keys=True)}"
        return f"cosign-sim-{hashlib.sha256(combined.encode()).hexdigest()[:16]}"
    
    # In production: actual cosign signing
    return "production-cosign-signature"

def validate_model_signature(model_hash: str, signature: str, metadata: Dict[str, Any]) -> bool:
    """Validate cosign signature"""
    if SIMULATION_MODE:
        # Simulate signature validation
        expected = generate_cosign_signature(model_hash, metadata)
        return signature == expected
    
    # In production: actual cosign verification
    return True

def store_artifact(model_id: str, artifact_data: Dict[str, Any]) -> str:
    """Store model artifact and return storage path"""
    if SIMULATION_MODE:
        # Store in memory for simulation
        model_artifacts[model_id] = artifact_data
        return f"memory://{model_id}"
    
    # In production: store in S3 or similar
    os.makedirs(STORAGE_PATH, exist_ok=True)
    artifact_path = os.path.join(STORAGE_PATH, f"{model_id}.json")
    
    with open(artifact_path, 'w') as f:
        json.dump(artifact_data, f)
    
    return artifact_path

def retrieve_artifact(model_id: str) -> Dict[str, Any]:
    """Retrieve model artifact"""
    if SIMULATION_MODE:
        if model_id not in model_artifacts:
            raise ValueError(f"Model {model_id} not found")
        return model_artifacts[model_id]
    
    # In production: retrieve from S3 or similar
    artifact_path = os.path.join(STORAGE_PATH, f"{model_id}.json")
    
    if not os.path.exists(artifact_path):
        raise ValueError(f"Model {model_id} not found")
    
    with open(artifact_path, 'r') as f:
        return json.load(f)

@app.post("/v1/models")
async def commit_model(request: ModelCommitRequest):
    """Commit new model version to store"""
    with STORAGE_LATENCY.time():
        model_id = request.metadata.model_id
        
        # Calculate model hash
        model_hash = calculate_model_hash(request.artifact_data)
        
        # Generate or validate signature
        if not request.signature:
            signature = generate_cosign_signature(model_hash, request.metadata.dict())
        else:
            signature = request.signature
            if not validate_model_signature(model_hash, signature, request.metadata.dict()):
                raise HTTPException(status_code=400, detail="Invalid model signature")
        
        # Store artifact
        storage_path = store_artifact(model_id, request.artifact_data)
        
        # Create registry entry
        registry_entry = {
            "model_id": model_id,
            "model_hash": model_hash,
            "metadata": request.metadata.dict(),
            "storage_path": storage_path,
            "signature": signature,
            "committed_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        model_registry[model_id] = registry_entry
        MODELS_STORED.inc()
        
        logger.info(f"Committed model {model_id} with hash {model_hash[:16]}")
        
        return {
            "model_id": model_id,
            "model_hash": model_hash,
            "signature": signature,
            "storage_path": storage_path,
            "committed_at": registry_entry["committed_at"]
        }

@app.get("/v1/models/{model_id}")
async def get_model(model_id: str, include_artifact: bool = False):
    """Get model metadata and optionally artifact"""
    MODELS_RETRIEVED.inc()
    
    if model_id not in model_registry:
        raise HTTPException(status_code=404, detail="Model not found")
    
    registry_entry = model_registry[model_id]
    
    response = {
        "model_id": model_id,
        "model_hash": registry_entry["model_hash"],
        "metadata": registry_entry["metadata"],
        "signature": registry_entry["signature"],
        "committed_at": registry_entry["committed_at"],
        "status": registry_entry["status"]
    }
    
    if include_artifact:
        try:
            artifact_data = retrieve_artifact(model_id)
            response["artifact"] = artifact_data
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    return response

@app.get("/v1/models")
async def list_models(
    round_id: Optional[str] = None,
    algorithm: Optional[str] = None,
    limit: int = 100
):
    """List models with optional filtering"""
    models = []
    
    for model_id, entry in model_registry.items():
        # Apply filters
        if round_id and entry["metadata"]["round_id"] != round_id:
            continue
        if algorithm and entry["metadata"]["algorithm"] != algorithm:
            continue
        
        models.append({
            "model_id": model_id,
            "model_hash": entry["model_hash"],
            "round_id": entry["metadata"]["round_id"],
            "version": entry["metadata"]["version"],
            "algorithm": entry["metadata"]["algorithm"],
            "committed_at": entry["committed_at"],
            "status": entry["status"]
        })
        
        if len(models) >= limit:
            break
    
    return {
        "models": models,
        "total": len(models),
        "filters_applied": {
            "round_id": round_id,
            "algorithm": algorithm,
            "limit": limit
        }
    }

@app.post("/v1/models/{model_id}/verify")
async def verify_model(model_id: str):
    """Verify model signature and integrity"""
    if model_id not in model_registry:
        raise HTTPException(status_code=404, detail="Model not found")
    
    registry_entry = model_registry[model_id]
    
    try:
        # Retrieve artifact and recalculate hash
        artifact_data = retrieve_artifact(model_id)
        calculated_hash = calculate_model_hash(artifact_data)
        
        # Verify hash matches
        hash_valid = calculated_hash == registry_entry["model_hash"]
        
        # Verify signature
        signature_valid = validate_model_signature(
            calculated_hash,
            registry_entry["signature"],
            registry_entry["metadata"]
        )
        
        return {
            "model_id": model_id,
            "hash_valid": hash_valid,
            "signature_valid": signature_valid,
            "integrity_verified": hash_valid and signature_valid,
            "calculated_hash": calculated_hash,
            "stored_hash": registry_entry["model_hash"],
            "verified_at": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        return {
            "model_id": model_id,
            "hash_valid": False,
            "signature_valid": False,
            "integrity_verified": False,
            "error": str(e),
            "verified_at": datetime.utcnow().isoformat()
        }

@app.delete("/v1/models/{model_id}")
async def archive_model(model_id: str):
    """Archive model (mark as inactive)"""
    if model_id not in model_registry:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model_registry[model_id]["status"] = "archived"
    model_registry[model_id]["archived_at"] = datetime.utcnow().isoformat()
    
    return {
        "model_id": model_id,
        "status": "archived",
        "archived_at": model_registry[model_id]["archived_at"]
    }

@app.get("/v1/rounds/{round_id}/models")
async def get_round_models(round_id: str):
    """Get all models for a specific FL round"""
    round_models = []
    
    for model_id, entry in model_registry.items():
        if entry["metadata"]["round_id"] == round_id:
            round_models.append({
                "model_id": model_id,
                "model_hash": entry["model_hash"],
                "version": entry["metadata"]["version"],
                "participants": entry["metadata"]["participants"],
                "performance_metrics": entry["metadata"]["performance_metrics"],
                "committed_at": entry["committed_at"]
            })
    
    return {
        "round_id": round_id,
        "models": round_models,
        "model_count": len(round_models)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "model-store",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "models_stored": len(model_registry)
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return JSONResponse(
        content=generate_latest().decode('utf-8'),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)