from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI(title="ATOM Model Registry", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class ModelMetadata(BaseModel):
    model_id: str
    version: str
    framework: str
    size_gb: float
    description: str = ""

# In-memory model registry
models = {
    "llama-7b": {"version": "v1.0", "framework": "pytorch", "size_gb": 13.5, "status": "active"},
    "stable-diffusion-xl": {"version": "v1.0", "framework": "diffusers", "size_gb": 6.9, "status": "active"}
}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "model-registry", "simulation": SIMULATION_MODE}

@app.post("/models/register")
def register_model(model: ModelMetadata):
    """Register new model"""
    if SIMULATION_MODE:
        models[model.model_id] = {
            "version": model.version,
            "framework": model.framework,
            "size_gb": model.size_gb,
            "description": model.description,
            "status": "active",
            "registered_at": datetime.now().isoformat()
        }
        
        return {
            "model_id": model.model_id,
            "status": "registered",
            "download_url": f"https://models.atom.cloud/{model.model_id}/{model.version}",
            "simulation": True
        }
    
    return {"error": "Model registration unavailable"}

@app.get("/models")
def list_models():
    """List registered models"""
    if SIMULATION_MODE:
        return {"models": models, "total": len(models)}
    
    return {"error": "Model listing unavailable"}

@app.get("/models/{model_id}")
def get_model(model_id: str):
    """Get model metadata"""
    if SIMULATION_MODE:
        if model_id in models:
            return {"model_id": model_id, **models[model_id]}
        return {"error": "Model not found"}
    
    return {"error": "Model retrieval unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8614)