from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI(title="ATOM Neural Autoscaler", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class ScalingMetrics(BaseModel):
    deployment_id: str
    cpu_usage: float
    gpu_usage: float
    memory_usage: float
    request_rate: float

@app.get("/health")
def health():
    return {"status": "healthy", "service": "neural-autoscaler", "simulation": SIMULATION_MODE}

@app.post("/scale/evaluate")
def evaluate_scaling(metrics: ScalingMetrics):
    """Evaluate if scaling is needed"""
    if SIMULATION_MODE:
        scale_up = metrics.gpu_usage > 80 or metrics.request_rate > 100
        scale_down = metrics.gpu_usage < 20 and metrics.request_rate < 10
        
        action = "none"
        if scale_up:
            action = "scale_up"
        elif scale_down:
            action = "scale_down"
        
        return {
            "deployment_id": metrics.deployment_id,
            "action": action,
            "current_replicas": 2,
            "target_replicas": 3 if scale_up else (1 if scale_down else 2),
            "reason": f"GPU usage: {metrics.gpu_usage}%, Request rate: {metrics.request_rate}/s",
            "evaluated_at": datetime.now().isoformat()
        }
    
    return {"error": "Scaling evaluation unavailable"}

@app.post("/scale/execute")
def execute_scaling(deployment_id: str, target_replicas: int):
    """Execute scaling action"""
    if SIMULATION_MODE:
        return {
            "deployment_id": deployment_id,
            "target_replicas": target_replicas,
            "status": "scaling",
            "estimated_completion": "2024-01-15T10:05:00Z"
        }
    
    return {"error": "Scaling execution unavailable"}

@app.get("/scale/status")
def scaling_status():
    """Get autoscaling status"""
    if SIMULATION_MODE:
        return {
            "active_scalers": 3,
            "scaling_events_24h": 12,
            "avg_scale_time_seconds": 45,
            "policy": "reactive"
        }
    
    return {"error": "Scaling status unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8612)