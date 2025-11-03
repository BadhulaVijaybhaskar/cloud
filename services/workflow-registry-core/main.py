#!/usr/bin/env python3
"""
Workflow Registry Core Service - Workflow Management
Handles workflow metadata, versioning, and execution coordination
"""

import os
import json
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import redis
import asyncpg
from datetime import datetime
import uuid

# Environment Configuration
COMPONENT_NAME = os.getenv("COMPONENT_NAME", "workflow-registry-core")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8084"))
REDIS_URL = os.getenv("EVENT_BUS_URL", "redis://localhost:6379/1")
POSTGRES_URL = os.getenv("REGISTRY_DB_URL", "postgresql://user:pass@localhost:5432/registry")
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
LANGGRAPH_URL = os.getenv("LANGGRAPH_URL", "http://langgraph-core:8080")

app = FastAPI(title="Workflow Registry Core", version="1.0.0")

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

class WorkflowRegistry:
    """Core workflow registry management"""
    
    def __init__(self):
        self.workflows = {}
        self.executions = {}
    
    async def register_workflow(self, workflow_data: Dict[str, Any], tenant_id: str) -> str:
        """Register a new workflow"""
        workflow_id = workflow_data.get("id") or str(uuid.uuid4())
        
        workflow = {
            "id": workflow_id,
            "name": workflow_data.get("name", "Untitled Workflow"),
            "description": workflow_data.get("description", ""),
            "version": workflow_data.get("version", "1.0.0"),
            "tenant_id": tenant_id,
            "nodes": workflow_data.get("nodes", []),
            "edges": workflow_data.get("edges", []),
            "triggers": workflow_data.get("triggers", []),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        self.workflows[workflow_id] = workflow
        return workflow_id
    
    async def trigger_workflow(self, workflow_id: str, inputs: Dict[str, Any], tenant_id: str) -> str:
        """Trigger workflow execution"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        if workflow["tenant_id"] != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        execution_id = str(uuid.uuid4())
        
        execution = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "tenant_id": tenant_id,
            "inputs": inputs,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat(),
            "mode": "simulation" if SIMULATION_MODE else "live"
        }
        
        self.executions[execution_id] = execution
        
        if SIMULATION_MODE:
            # Simulate execution
            execution["status"] = "running"
            execution["langgraph_execution_id"] = f"sim_lg_{int(datetime.utcnow().timestamp())}"
        
        return execution_id
    
    def get_workflow(self, workflow_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID"""
        workflow = self.workflows.get(workflow_id)
        if workflow and workflow["tenant_id"] == tenant_id:
            return workflow
        return None
    
    def list_workflows(self, tenant_id: str) -> List[Dict[str, Any]]:
        """List workflows for tenant"""
        return [w for w in self.workflows.values() if w["tenant_id"] == tenant_id]
    
    def get_execution(self, execution_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get execution by ID"""
        execution = self.executions.get(execution_id)
        if execution and execution["tenant_id"] == tenant_id:
            return execution
        return None

# Initialize registry
registry = WorkflowRegistry()

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
        "registered_workflows": len(registry.workflows),
        "active_executions": len(registry.executions)
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    workflow_count = len(registry.workflows)
    execution_count = len(registry.executions)
    metrics = [
        f"# HELP workflow_registry_workflows_total Total registered workflows",
        f"# TYPE workflow_registry_workflows_total gauge",
        f"workflow_registry_workflows_total{{service=\"{COMPONENT_NAME}\"}} {workflow_count}",
        f"# HELP workflow_registry_executions_total Total workflow executions",
        f"# TYPE workflow_registry_executions_total gauge",
        f"workflow_registry_executions_total{{service=\"{COMPONENT_NAME}\"}} {execution_count}"
    ]
    return "\n".join(metrics)

@app.post("/v1/workflows")
async def register_workflow(request: Dict[str, Any]):
    """Register a new workflow"""
    try:
        tenant_id = request.get("tenant_id", "default")
        workflow_id = await registry.register_workflow(request, tenant_id)
        
        return {
            "workflow_id": workflow_id,
            "status": "registered",
            "tenant_id": tenant_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@app.get("/v1/workflows")
async def list_workflows(tenant_id: str = "default"):
    """List workflows for tenant"""
    workflows = registry.list_workflows(tenant_id)
    return {"workflows": workflows}

@app.get("/v1/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, tenant_id: str = "default"):
    """Get workflow by ID"""
    workflow = registry.get_workflow(workflow_id, tenant_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow

@app.post("/v1/trigger")
async def trigger_workflow(request: Dict[str, Any]):
    """Trigger workflow execution"""
    try:
        workflow_id = request.get("workflow_id")
        inputs = request.get("inputs", {})
        tenant_id = request.get("tenant_id", "default")
        
        if not workflow_id:
            raise HTTPException(status_code=400, detail="workflow_id is required")
        
        execution_id = await registry.trigger_workflow(workflow_id, inputs, tenant_id)
        
        return {
            "workflow_execution_id": execution_id,
            "status": "triggered",
            "workflow_id": workflow_id,
            "tenant_id": tenant_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trigger error: {str(e)}")

@app.get("/v1/executions/{execution_id}")
async def get_execution_status(execution_id: str, tenant_id: str = "default"):
    """Get execution status"""
    execution = registry.get_execution(execution_id, tenant_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)