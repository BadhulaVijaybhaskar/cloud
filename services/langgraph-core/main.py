#!/usr/bin/env python3
"""
LangGraph Core Service - Graph Execution Runtime
Handles graph execution, state management, and node scheduling
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import redis
import asyncpg
from datetime import datetime
import uuid

# Environment Configuration
COMPONENT_NAME = os.getenv("COMPONENT_NAME", "langgraph-core")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8080"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
POSTGRES_URL = os.getenv("LANGGRAPH_DB_URL", "postgresql://user:pass@localhost:5432/langgraph")
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

app = FastAPI(title="LangGraph Core", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if SIMULATION_MODE else ["https://*.atom-cloud.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global connections
redis_client = None
db_pool = None

class GraphExecutor:
    """Core graph execution engine"""
    
    def __init__(self):
        self.active_executions = {}
    
    async def execute_graph(self, graph_id: str, inputs: Dict[str, Any], tenant_id: str) -> str:
        """Execute a graph with given inputs"""
        execution_id = str(uuid.uuid4())
        
        if SIMULATION_MODE:
            # Simulate graph execution
            execution = {
                "id": execution_id,
                "graph_id": graph_id,
                "status": "running",
                "tenant_id": tenant_id,
                "inputs": inputs,
                "outputs": {},
                "created_at": datetime.utcnow().isoformat(),
                "mode": "simulation"
            }
            self.active_executions[execution_id] = execution
            
            # Simulate async completion
            asyncio.create_task(self._simulate_completion(execution_id))
            return execution_id
        
        # Real execution logic would go here
        execution = {
            "id": execution_id,
            "graph_id": graph_id,
            "status": "queued",
            "tenant_id": tenant_id,
            "inputs": inputs,
            "outputs": {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.active_executions[execution_id] = execution
        return execution_id
    
    async def _simulate_completion(self, execution_id: str):
        """Simulate graph execution completion"""
        await asyncio.sleep(2)  # Simulate processing time
        
        if execution_id in self.active_executions:
            self.active_executions[execution_id].update({
                "status": "completed",
                "outputs": {"result": "simulated_output", "nodes_executed": 5},
                "completed_at": datetime.utcnow().isoformat()
            })
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        return self.active_executions.get(execution_id)

# Initialize executor
executor = GraphExecutor()

@app.on_event("startup")
async def startup():
    global redis_client, db_pool
    
    if not SIMULATION_MODE:
        try:
            redis_client = redis.from_url(REDIS_URL)
            db_pool = await asyncpg.create_pool(POSTGRES_URL)
        except Exception as e:
            print(f"Database connection error: {e}")

@app.on_event("shutdown")
async def shutdown():
    if db_pool:
        await db_pool.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": COMPONENT_NAME,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "active_executions": len(executor.active_executions)
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    active_count = len(executor.active_executions)
    metrics = [
        f"# HELP langgraph_active_executions Active graph executions",
        f"# TYPE langgraph_active_executions gauge",
        f"langgraph_active_executions{{service=\"{COMPONENT_NAME}\"}} {active_count}",
        f"# HELP langgraph_requests_total Total execution requests",
        f"# TYPE langgraph_requests_total counter",
        f"langgraph_requests_total{{service=\"{COMPONENT_NAME}\"}} 0"
    ]
    return "\n".join(metrics)

@app.post("/v1/execute")
async def execute_graph(request: Dict[str, Any], background_tasks: BackgroundTasks):
    """Execute a graph"""
    try:
        graph_id = request.get("graph_id")
        inputs = request.get("inputs", {})
        tenant_id = request.get("tenant_id", "default")
        
        if not graph_id:
            raise HTTPException(status_code=400, detail="graph_id is required")
        
        execution_id = await executor.execute_graph(graph_id, inputs, tenant_id)
        
        return {
            "execution_id": execution_id,
            "status": "queued",
            "graph_id": graph_id,
            "tenant_id": tenant_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

@app.get("/v1/executions/{execution_id}")
async def get_execution_status(execution_id: str):
    """Get execution status"""
    execution = executor.get_execution_status(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution

@app.get("/v1/executions")
async def list_executions(tenant_id: Optional[str] = None):
    """List executions, optionally filtered by tenant"""
    executions = list(executor.active_executions.values())
    
    if tenant_id:
        executions = [e for e in executions if e.get("tenant_id") == tenant_id]
    
    return {"executions": executions}

@app.post("/v1/executions/{execution_id}/cancel")
async def cancel_execution(execution_id: str):
    """Cancel a running execution"""
    execution = executor.get_execution_status(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution["status"] in ["completed", "failed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Execution already finished")
    
    execution["status"] = "cancelled"
    execution["cancelled_at"] = datetime.utcnow().isoformat()
    
    return {"message": "Execution cancelled", "execution_id": execution_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)