from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI(title="ATOM GPU Resource Manager", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class GPUNode(BaseModel):
    node_id: str
    gpu_count: int
    gpu_type: str = "A100"
    memory_gb: int = 40

# In-memory GPU registry for simulation
gpu_nodes = {
    "gpu-node-1": {"gpu_count": 8, "gpu_type": "A100", "memory_gb": 320, "available": 6},
    "gpu-node-2": {"gpu_count": 4, "gpu_type": "V100", "memory_gb": 128, "available": 4}
}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "gpu-resource-manager", "simulation": SIMULATION_MODE}

@app.post("/gpu/register")
def register_gpu_node(node: GPUNode):
    """Register GPU node"""
    if SIMULATION_MODE:
        gpu_nodes[node.node_id] = {
            "gpu_count": node.gpu_count,
            "gpu_type": node.gpu_type,
            "memory_gb": node.memory_gb,
            "available": node.gpu_count,
            "registered_at": datetime.now().isoformat()
        }
        return {"node_id": node.node_id, "status": "registered", "simulation": True}
    
    return {"error": "GPU registration unavailable"}

@app.get("/gpu/nodes")
def list_gpu_nodes():
    """List available GPU nodes"""
    if SIMULATION_MODE:
        return {"nodes": gpu_nodes, "total_gpus": sum(n["gpu_count"] for n in gpu_nodes.values())}
    
    return {"error": "GPU listing unavailable"}

@app.post("/gpu/allocate")
def allocate_gpus(job_id: str, gpu_count: int):
    """Allocate GPUs for job"""
    if SIMULATION_MODE:
        for node_id, node in gpu_nodes.items():
            if node["available"] >= gpu_count:
                node["available"] -= gpu_count
                return {
                    "job_id": job_id,
                    "allocated_node": node_id,
                    "allocated_gpus": gpu_count,
                    "status": "allocated"
                }
        
        return {"error": "Insufficient GPU resources"}
    
    return {"error": "GPU allocation unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8610)