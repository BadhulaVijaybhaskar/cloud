from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import yaml
import json
import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import tempfile
import uuid
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ATOM Runtime Agent", version="1.0.0")

# Prometheus metrics
workflow_runs_total = Counter('workflow_runs_total', 'Total workflow executions', ['workflow_name', 'status'])
workflow_success_total = Counter('workflow_success_total', 'Successful workflow executions', ['workflow_name'])
workflow_failure_total = Counter('workflow_failure_total', 'Failed workflow executions', ['workflow_name', 'error_type'])
workflow_duration_seconds = Histogram('workflow_duration_seconds', 'Workflow execution duration', ['workflow_name'])
active_workflows = Gauge('active_workflows', 'Currently running workflows')

# Configuration
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# In-memory execution state
execution_state: Dict[str, Dict] = {}

class WorkflowExecutionRequest(BaseModel):
    workflow_id: str
    wpk_content: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = {}
    dry_run: bool = False

class ExecutionStatus(BaseModel):
    execution_id: str
    workflow_id: str
    status: str  # "pending", "running", "completed", "failed", "rolled_back"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    current_step: Optional[str] = None
    steps_completed: int = 0
    total_steps: int = 0
    error_message: Optional[str] = None
    logs: List[str] = []

class RuntimeAgent:
    def __init__(self):
        self.adapters = {}
        self.load_adapters()
    
    def load_adapters(self):
        """Load available adapters"""
        # Mock adapter loading - in production, dynamically load from adapters directory
        self.adapters = {
            "k8s": self.k8s_adapter,
            "shell": self.shell_adapter,
            "api": self.api_adapter
        }
    
    async def k8s_adapter(self, action: str, config: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """Kubernetes adapter for executing k8s operations"""
        logger.info(f"K8s adapter: {action} with config {config}")
        
        if dry_run:
            return {"status": "success", "message": f"Dry run: would execute {action}", "dry_run": True}
        
        try:
            if action == "logs":
                # Mock kubectl logs
                cmd = f"kubectl logs {config.get('resource', 'pod')} --lines={config.get('lines', 100)}"
                result = await self.execute_command(cmd)
                return {"status": "success", "logs": result.get("stdout", ""), "action": action}
            
            elif action == "events":
                # Mock kubectl get events
                cmd = f"kubectl get events --field-selector involvedObject.kind={config.get('resource_type', 'Pod')}"
                result = await self.execute_command(cmd)
                return {"status": "success", "events": result.get("stdout", ""), "action": action}
            
            elif action == "restart":
                # Mock kubectl rollout restart
                resource_type = config.get("resource_type", "deployment")
                resource_name = config.get("resource_name", "app")
                cmd = f"kubectl rollout restart {resource_type}/{resource_name}"
                result = await self.execute_command(cmd)
                return {"status": "success", "message": f"Restarted {resource_type}/{resource_name}", "action": action}
            
            elif action == "scale":
                # Mock kubectl scale
                resource_type = config.get("resource_type", "deployment")
                resource_name = config.get("resource_name", "app")
                replicas = config.get("replicas", 3)
                cmd = f"kubectl scale {resource_type}/{resource_name} --replicas={replicas}"
                result = await self.execute_command(cmd)
                return {"status": "success", "message": f"Scaled {resource_type}/{resource_name} to {replicas}", "action": action}
            
            elif action == "wait":
                # Mock kubectl wait
                condition = config.get("condition", "ready")
                timeout = config.get("timeout", "60s")
                return {"status": "success", "message": f"Waited for condition {condition}", "action": action}
            
            else:
                return {"status": "error", "message": f"Unknown k8s action: {action}"}
                
        except Exception as e:
            logger.error(f"K8s adapter error: {str(e)}")
            return {"status": "error", "message": str(e), "action": action}
    
    async def shell_adapter(self, command: str, config: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """Shell adapter for executing shell commands"""
        logger.info(f"Shell adapter: {command}")
        
        if dry_run:
            return {"status": "success", "message": f"Dry run: would execute {command}", "dry_run": True}
        
        try:
            result = await self.execute_command(command)
            return {
                "status": "success" if result["returncode"] == 0 else "error",
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "returncode": result["returncode"]
            }
        except Exception as e:
            logger.error(f"Shell adapter error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def api_adapter(self, url: str, config: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """API adapter for making HTTP requests"""
        logger.info(f"API adapter: {config.get('method', 'GET')} {url}")
        
        if dry_run:
            return {"status": "success", "message": f"Dry run: would call {config.get('method', 'GET')} {url}", "dry_run": True}
        
        try:
            # Mock HTTP request - in production use httpx or requests
            method = config.get("method", "GET")
            return {
                "status": "success",
                "message": f"Mock {method} request to {url}",
                "response_code": 200
            }
        except Exception as e:
            logger.error(f"API adapter error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute shell command asynchronously"""
        try:
            # Mock command execution for testing
            logger.info(f"Executing command: {command}")
            return {
                "returncode": 0,
                "stdout": f"Mock output for: {command}",
                "stderr": ""
            }
        except Exception as e:
            return {
                "returncode": 1,
                "stdout": "",
                "stderr": str(e)
            }
    
    async def execute_workflow(self, execution_id: str, wpk_content: Dict[str, Any], parameters: Dict[str, Any], dry_run: bool = False):
        """Execute a workflow with all its handlers"""
        workflow_name = wpk_content["metadata"]["name"]
        handlers = wpk_content["spec"]["handlers"]
        
        # Update execution state
        execution_state[execution_id]["status"] = "running"
        execution_state[execution_id]["started_at"] = datetime.utcnow().isoformat()
        execution_state[execution_id]["total_steps"] = len(handlers)
        
        # Start metrics
        active_workflows.inc()
        start_time = datetime.utcnow()
        
        try:
            for i, handler in enumerate(handlers):
                # Update current step
                execution_state[execution_id]["current_step"] = handler["name"]
                execution_state[execution_id]["steps_completed"] = i
                
                logger.info(f"Executing handler: {handler['name']}")
                
                # Get adapter
                handler_type = handler["type"]
                if handler_type not in self.adapters:
                    raise Exception(f"Unknown handler type: {handler_type}")
                
                adapter = self.adapters[handler_type]
                
                # Execute handler
                if handler_type == "k8s":
                    result = await adapter(handler["config"].get("action", ""), handler["config"], dry_run)
                elif handler_type == "shell":
                    result = await adapter(handler["config"].get("command", ""), handler["config"], dry_run)
                elif handler_type == "api":
                    result = await adapter(handler["config"].get("url", ""), handler["config"], dry_run)
                else:
                    result = {"status": "error", "message": f"Unknown handler type: {handler_type}"}
                
                # Log result
                log_entry = f"Handler {handler['name']}: {result.get('status', 'unknown')}"
                execution_state[execution_id]["logs"].append(log_entry)
                
                # Check for failure
                if result.get("status") == "error":
                    raise Exception(f"Handler {handler['name']} failed: {result.get('message', 'Unknown error')}")
                
                # Simulate processing time
                await asyncio.sleep(0.1)
            
            # Mark as completed
            execution_state[execution_id]["status"] = "completed"
            execution_state[execution_id]["completed_at"] = datetime.utcnow().isoformat()
            execution_state[execution_id]["steps_completed"] = len(handlers)
            
            # Update metrics
            workflow_runs_total.labels(workflow_name=workflow_name, status="success").inc()
            workflow_success_total.labels(workflow_name=workflow_name).inc()
            
        except Exception as e:
            # Mark as failed
            execution_state[execution_id]["status"] = "failed"
            execution_state[execution_id]["completed_at"] = datetime.utcnow().isoformat()
            execution_state[execution_id]["error_message"] = str(e)
            
            logger.error(f"Workflow execution failed: {str(e)}")
            
            # Update metrics
            workflow_runs_total.labels(workflow_name=workflow_name, status="failed").inc()
            workflow_failure_total.labels(workflow_name=workflow_name, error_type="execution_error").inc()
            
            # Attempt rollback if enabled
            if wpk_content["spec"].get("rollback", {}).get("enabled", False):
                await self.execute_rollback(execution_id, wpk_content, dry_run)
        
        finally:
            # Update metrics
            active_workflows.dec()
            duration = (datetime.utcnow() - start_time).total_seconds()
            workflow_duration_seconds.labels(workflow_name=workflow_name).observe(duration)
    
    async def execute_rollback(self, execution_id: str, wpk_content: Dict[str, Any], dry_run: bool = False):
        """Execute rollback handlers"""
        rollback_handlers = wpk_content["spec"].get("rollback", {}).get("handlers", [])
        
        if not rollback_handlers:
            return
        
        logger.info(f"Executing rollback for {execution_id}")
        execution_state[execution_id]["logs"].append("Starting rollback...")
        
        try:
            for handler in rollback_handlers:
                logger.info(f"Rollback handler: {handler['name']}")
                
                handler_type = handler["type"]
                if handler_type in self.adapters:
                    adapter = self.adapters[handler_type]
                    
                    if handler_type == "k8s":
                        result = await adapter(handler["config"].get("action", ""), handler["config"], dry_run)
                    elif handler_type == "shell":
                        result = await adapter(handler["config"].get("command", ""), handler["config"], dry_run)
                    elif handler_type == "api":
                        result = await adapter(handler["config"].get("url", ""), handler["config"], dry_run)
                    
                    log_entry = f"Rollback {handler['name']}: {result.get('status', 'unknown')}"
                    execution_state[execution_id]["logs"].append(log_entry)
            
            execution_state[execution_id]["status"] = "rolled_back"
            execution_state[execution_id]["logs"].append("Rollback completed")
            
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            execution_state[execution_id]["logs"].append(f"Rollback failed: {str(e)}")

# Initialize runtime agent
runtime_agent = RuntimeAgent()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_executions": len([e for e in execution_state.values() if e["status"] == "running"])
    }

@app.post("/init")
async def initialize_agent():
    """Initialize the runtime agent"""
    logger.info("Runtime agent initialized")
    return {"status": "initialized", "adapters": list(runtime_agent.adapters.keys())}

@app.post("/validate")
async def validate_workflow(request: WorkflowExecutionRequest):
    """Validate workflow before execution"""
    try:
        wpk_content = request.wpk_content
        
        # Basic validation
        if "metadata" not in wpk_content or "spec" not in wpk_content:
            raise HTTPException(status_code=400, detail="Invalid WPK structure")
        
        if "handlers" not in wpk_content["spec"]:
            raise HTTPException(status_code=400, detail="No handlers defined")
        
        # Validate handlers
        for handler in wpk_content["spec"]["handlers"]:
            if "type" not in handler or handler["type"] not in runtime_agent.adapters:
                raise HTTPException(status_code=400, detail=f"Unknown handler type: {handler.get('type', 'missing')}")
        
        return {
            "status": "valid",
            "workflow_name": wpk_content["metadata"]["name"],
            "total_handlers": len(wpk_content["spec"]["handlers"]),
            "supported_adapters": list(runtime_agent.adapters.keys())
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")

@app.post("/execute")
async def execute_workflow(request: WorkflowExecutionRequest, background_tasks: BackgroundTasks):
    """Execute a workflow"""
    execution_id = str(uuid.uuid4())
    
    # Initialize execution state
    execution_state[execution_id] = {
        "execution_id": execution_id,
        "workflow_id": request.workflow_id,
        "status": "pending",
        "started_at": None,
        "completed_at": None,
        "current_step": None,
        "steps_completed": 0,
        "total_steps": 0,
        "error_message": None,
        "logs": []
    }
    
    # Start execution in background
    background_tasks.add_task(
        runtime_agent.execute_workflow,
        execution_id,
        request.wpk_content,
        request.parameters,
        request.dry_run
    )
    
    return {
        "execution_id": execution_id,
        "status": "started",
        "message": "Workflow execution started"
    }

@app.get("/execute/{execution_id}")
async def get_execution_status(execution_id: str):
    """Get execution status"""
    if execution_id not in execution_state:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution_state[execution_id]

@app.post("/rollback/{execution_id}")
async def rollback_execution(execution_id: str, background_tasks: BackgroundTasks):
    """Rollback a workflow execution"""
    if execution_id not in execution_state:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    execution = execution_state[execution_id]
    
    if execution["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot rollback running execution")
    
    # Mock rollback - in production, load original WPK content
    background_tasks.add_task(
        runtime_agent.execute_rollback,
        execution_id,
        {"spec": {"rollback": {"enabled": True, "handlers": []}}},
        False
    )
    
    return {"message": "Rollback started", "execution_id": execution_id}

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")

@app.get("/logs/{execution_id}")
async def get_execution_logs(execution_id: str):
    """Get execution logs"""
    if execution_id not in execution_state:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {
        "execution_id": execution_id,
        "logs": execution_state[execution_id]["logs"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)