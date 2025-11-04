#!/usr/bin/env python3
"""
ATOM Agent Registry - Port 8102
Agent manifest and execution policy management per J.3 spec
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any

app = FastAPI(title="ATOM Agent Registry", version="1.0.0")

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

class AgentManifest(BaseModel):
    name: str
    vendor_id: str
    version: str
    description: str
    execution_policy: Dict[str, Any]
    capabilities: List[str] = []
    resource_requirements: Dict[str, Any] = {}
    safety_constraints: Dict[str, Any] = {}

# Simulated agent storage
agents_db = {}
test_runs = {}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "agent-registry", 
        "port": 8102,
        "simulation_mode": SIMULATION_MODE
    }

@app.post("/v1/agents")
async def register_agent(agent: AgentManifest):
    """Register agent with manifest + execution policy"""
    
    agent_id = str(uuid.uuid4())
    
    # Validate execution policy
    required_fields = ["max_runtime_seconds", "allowed_actions", "resource_limits"]
    for field in required_fields:
        if field not in agent.execution_policy:
            raise HTTPException(status_code=400, detail=f"Missing execution policy field: {field}")
    
    agent_data = {
        "id": agent_id,
        "manifest": agent.dict(),
        "status": "registered",
        "created_at": datetime.utcnow().isoformat(),
        "test_runs": 0,
        "governance_status": "pending_review"
    }
    
    agents_db[agent_id] = agent_data
    
    return {
        "agent_id": agent_id,
        "status": "registered",
        "message": "Agent registered successfully"
    }

@app.get("/v1/agents")
async def list_agents(vendor: str = None, capability: str = None):
    """List registered agents"""
    
    agents = list(agents_db.values())
    
    if vendor:
        agents = [a for a in agents if a["manifest"]["vendor_id"] == vendor]
    
    if capability:
        agents = [a for a in agents if capability in a["manifest"]["capabilities"]]
    
    return {
        "agents": agents,
        "total": len(agents),
        "simulation_mode": SIMULATION_MODE
    }

@app.post("/v1/agents/{agent_id}/test-run")
async def test_run_agent(agent_id: str, test_config: Dict[str, Any] = {}):
    """Run agent in sandbox environment"""
    
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_db[agent_id]
    run_id = str(uuid.uuid4())[:16]
    
    # Simulate sandbox execution
    test_run = {
        "run_id": run_id,
        "agent_id": agent_id,
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "config": test_config,
        "simulation_mode": SIMULATION_MODE
    }
    
    test_runs[run_id] = test_run
    
    # Simulate execution completion
    import random
    success = random.choice([True, True, True, False])  # 75% success rate
    
    test_runs[run_id].update({
        "status": "completed" if success else "failed",
        "completed_at": datetime.utcnow().isoformat(),
        "result": {
            "success": success,
            "execution_time_ms": random.randint(100, 5000),
            "resource_usage": {
                "cpu_percent": random.randint(10, 80),
                "memory_mb": random.randint(50, 500)
            },
            "output": "Agent executed successfully" if success else "Agent execution failed"
        }
    })
    
    # Update agent test count
    agents_db[agent_id]["test_runs"] += 1
    
    return {
        "run_id": run_id,
        "status": test_runs[run_id]["status"],
        "agent_id": agent_id,
        "simulation_mode": SIMULATION_MODE
    }

@app.get("/v1/agents/{agent_id}/runs")
async def get_agent_runs(agent_id: str):
    """Get test run history for agent"""
    
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    runs = [run for run in test_runs.values() if run["agent_id"] == agent_id]
    runs.sort(key=lambda x: x["started_at"], reverse=True)
    
    return {
        "agent_id": agent_id,
        "runs": runs,
        "total_runs": len(runs)
    }

@app.get("/v1/runs/{run_id}")
async def get_run_result(run_id: str):
    """Get test run result"""
    
    if run_id not in test_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return test_runs[run_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8102)