#!/usr/bin/env python3
"""
ATOM Marketplace Core - J.3 Specification Implementation
Publish API that enqueues publish jobs per spec
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import hashlib
import time
from datetime import datetime

app = FastAPI(title="ATOM Marketplace Core", version="1.0.0")

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
MODEL_ARTIFACT_BUCKET = os.getenv('MODEL_ARTIFACT_BUCKET', 'atom-models-sim')
BILLING_SERVICE_URL = os.getenv('BILLING_SERVICE_URL', 'http://localhost:8200')

class PublishModel(BaseModel):
    name: str
    vendor_id: str
    version: str
    kind: str = "model"  # model|agent
    description: str
    artifact_url: str
    license: str = "MIT"
    tags: List[str] = []
    rationale: str = ""
    safety_metadata: dict = {}

# Job queue simulation
publish_jobs = {}
models_registry = {}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "marketplace-core",
        "simulation_mode": SIMULATION_MODE,
        "port": 8100
    }

@app.post("/v1/publish/model")
async def publish_model(model: PublishModel, background_tasks: BackgroundTasks):
    """
    Publish model per J.3 spec:
    - Accepts metadata + artifact
    - Runs pre-publish checks (P1, P5)
    - Stores in MODEL_ARTIFACT_BUCKET
    - Registers in model-registry
    - Creates billing hooks
    """
    
    # Generate job ID
    job_id = str(uuid.uuid4())[:16]
    
    # Pre-publish checks (simulated)
    checks = {
        "p1_pii_check": "PASS",  # No PII in metadata
        "p5_bias_check": "PASS",  # Bias validation
        "license_validation": "PASS" if model.license in ["MIT", "Apache-2.0", "proprietary"] else "FAIL"
    }
    
    if checks["license_validation"] == "FAIL":
        raise HTTPException(status_code=400, detail="Invalid license")
    
    # Create publish job
    job = {
        "job_id": job_id,
        "model": model.dict(),
        "status": "queued",
        "checks": checks,
        "created_at": datetime.utcnow().isoformat(),
        "artifact_bucket": MODEL_ARTIFACT_BUCKET
    }
    
    publish_jobs[job_id] = job
    
    # Queue background processing
    background_tasks.add_task(process_publish_job, job_id)
    
    return {
        "job_id": job_id,
        "status": "accepted",
        "message": "Model publish job queued"
    }, 202

async def process_publish_job(job_id: str):
    """Background job processor"""
    
    if job_id not in publish_jobs:
        return
    
    job = publish_jobs[job_id]
    model = job["model"]
    
    # Simulate artifact storage
    if SIMULATION_MODE:
        artifact_path = f"s3://{MODEL_ARTIFACT_BUCKET}/{model['vendor_id']}/{model['name']}/{model['version']}/model.tar.gz"
        checksum = hashlib.sha256(f"{model['name']}{model['version']}".encode()).hexdigest()
    else:
        # Real S3 upload would happen here
        artifact_path = f"s3://{MODEL_ARTIFACT_BUCKET}/{model['vendor_id']}/{model['name']}/{model['version']}/model.tar.gz"
        checksum = "real_checksum"
    
    # Register in model registry
    model_id = str(uuid.uuid4())
    models_registry[model_id] = {
        "id": model_id,
        "vendor_id": model["vendor_id"],
        "name": model["name"],
        "version": model["version"],
        "artifact_path": artifact_path,
        "checksum": checksum,
        "status": "published",
        "published_at": datetime.utcnow().isoformat(),
        "governance_status": "approved"
    }
    
    # Update job status
    publish_jobs[job_id]["status"] = "completed"
    publish_jobs[job_id]["model_id"] = model_id
    
    # Emit marketplace event (simulated)
    event = {
        "event": "marketplace.model.published",
        "model_id": model_id,
        "vendor_id": model["vendor_id"],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print(f"Event emitted: {event}")

@app.get("/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get publish job status"""
    
    if job_id not in publish_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return publish_jobs[job_id]

@app.get("/v1/models")
async def list_models(tags: Optional[str] = None, vendor: Optional[str] = None):
    """List published models"""
    
    models = list(models_registry.values())
    
    if vendor:
        models = [m for m in models if m["vendor_id"] == vendor]
    
    return {
        "models": models,
        "total": len(models),
        "simulation_mode": SIMULATION_MODE
    }

@app.get("/v1/models/{model_id}")
async def get_model(model_id: str):
    """Get model metadata"""
    
    if model_id not in models_registry:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return models_registry[model_id]

@app.post("/v1/meter")
async def meter_usage(usage: dict):
    """Billing hook for usage metering"""
    
    # Simulate billing event
    meter_event = {
        "project_id": usage.get("project_id"),
        "model_id": usage.get("model_id"),
        "units": usage.get("units", 1),
        "cost_center": usage.get("cost_center", "default"),
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE
    }
    
    print(f"Billing event: {meter_event}")
    
    return {"status": "metered", "event": meter_event}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)