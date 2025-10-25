from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import yaml
import json
import os
import hashlib
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import jsonschema
import uvicorn
from validator import WorkflowValidator, create_validator
from cosign_enforcer import create_cosign_enforcer
from validator.static_validator import create_static_validator
from validator.policy_engine import create_policy_engine
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Add langgraph hooks to path for run history integration
sys.path.append(str(Path(__file__).parent.parent.parent / "langgraph" / "hooks"))

app = FastAPI(title="ATOM Workflow Registry", version="1.0.0")
security = HTTPBearer()

# Configuration
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
WORKFLOWS_FILE = DATA_DIR / "workflows.json"
COSIGN_PUBLIC_KEY = os.getenv("COSIGN_PUBLIC_KEY", "")

# Initialize workflows storage
if not WORKFLOWS_FILE.exists():
    with open(WORKFLOWS_FILE, 'w') as f:
        json.dump({}, f)

# Initialize validator, cosign enforcer, static validator, and policy engine
validator = create_validator()
cosign_enforcer = create_cosign_enforcer()
static_validator = create_static_validator()
policy_engine = create_policy_engine()

def load_wpk_schema():
    """Load WPK validation schema"""
    schema = {
        "type": "object",
        "required": ["apiVersion", "kind", "metadata", "spec"],
        "properties": {
            "apiVersion": {"type": "string", "enum": ["v1"]},
            "kind": {"type": "string", "enum": ["WorkflowPackage"]},
            "metadata": {
                "type": "object",
                "required": ["name", "version", "description", "author"],
                "properties": {
                    "name": {"type": "string", "pattern": "^[a-z0-9-]+$"},
                    "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
                    "description": {"type": "string"},
                    "author": {"type": "string"},
                    "signature": {"type": "string"}
                }
            },
            "spec": {
                "type": "object",
                "required": ["runtime", "safety", "handlers"],
                "properties": {
                    "runtime": {"type": "object", "required": ["type"]},
                    "safety": {"type": "object", "required": ["mode"]},
                    "handlers": {"type": "array", "minItems": 1}
                }
            }
        }
    }
    return schema

def validate_wpk(wpk_data: dict) -> bool:
    """Validate WPK against schema"""
    schema = load_wpk_schema()
    try:
        jsonschema.validate(wpk_data, schema)
        return True
    except jsonschema.ValidationError:
        return False

def verify_cosign_signature(wpk_content: bytes, signature: str) -> bool:
    """Verify cosign signature using cosign enforcer"""
    return cosign_enforcer.verify_wpk_signature(wpk_content, signature)

def load_workflows() -> Dict:
    """Load workflows from storage"""
    with open(WORKFLOWS_FILE, 'r') as f:
        return json.load(f)

def save_workflows(workflows: Dict):
    """Save workflows to storage"""
    with open(WORKFLOWS_FILE, 'w') as f:
        json.dump(workflows, f, indent=2)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/workflows")
async def register_workflow(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Register a new workflow package"""
    
    # Read and parse WPK file
    content = await file.read()
    try:
        wpk_data = yaml.safe_load(content)
    except yaml.YAMLError:
        raise HTTPException(status_code=400, detail="Invalid YAML format")
    
    # Validate WPK schema
    if not validate_wpk(wpk_data):
        raise HTTPException(status_code=400, detail="Invalid WPK schema")
    
    # Check for signature (enforce cosign)
    signature = wpk_data.get("metadata", {}).get("signature", "")
    if not signature:
        raise HTTPException(status_code=400, detail="WPK must be signed with cosign")
    
    # Generate workflow ID
    workflow_name = wpk_data["metadata"]["name"]
    workflow_version = wpk_data["metadata"]["version"]
    workflow_id = f"{workflow_name}-{workflow_version}"
    
    # Save WPK file
    wpk_file_path = DATA_DIR / f"{workflow_id}.wpk.yaml"
    with open(wpk_file_path, 'wb') as f:
        f.write(content)
    
    # Verify signature using cosign
    if not verify_cosign_signature(content, signature):
        os.remove(wpk_file_path)
        raise HTTPException(status_code=400, detail="Invalid cosign signature")
    
    # Store workflow metadata
    workflows = load_workflows()
    workflows[workflow_id] = {
        "id": workflow_id,
        "name": workflow_name,
        "version": workflow_version,
        "description": wpk_data["metadata"]["description"],
        "author": wpk_data["metadata"]["author"],
        "created": wpk_data["metadata"].get("created", datetime.utcnow().isoformat()),
        "tags": wpk_data["metadata"].get("tags", []),
        "safety_mode": wpk_data["spec"]["safety"]["mode"],
        "runtime_type": wpk_data["spec"]["runtime"]["type"],
        "file_path": str(wpk_file_path),
        "signature": signature,
        "registered_at": datetime.utcnow().isoformat()
    }
    save_workflows(workflows)
    
    return {
        "message": "Workflow registered successfully",
        "workflow_id": workflow_id,
        "status": "registered"
    }

@app.get("/workflows")
async def list_workflows(
    tag: Optional[str] = None,
    runtime: Optional[str] = None,
    safety_mode: Optional[str] = None
):
    """List all registered workflows with optional filtering"""
    workflows = load_workflows()
    
    # Apply filters
    filtered_workflows = []
    for workflow in workflows.values():
        if tag and tag not in workflow.get("tags", []):
            continue
        if runtime and workflow.get("runtime_type") != runtime:
            continue
        if safety_mode and workflow.get("safety_mode") != safety_mode:
            continue
        filtered_workflows.append(workflow)
    
    return {
        "workflows": filtered_workflows,
        "total": len(filtered_workflows)
    }

@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get specific workflow details"""
    workflows = load_workflows()
    
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    
    # Load full WPK content
    try:
        with open(workflow["file_path"], 'r') as f:
            wpk_content = yaml.safe_load(f)
        workflow["wpk_content"] = wpk_content
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="WPK file not found")
    
    return workflow

@app.post("/workflows/{workflow_id}/sign")
async def sign_workflow(
    workflow_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Sign an existing workflow (admin only)"""
    workflows = load_workflows()
    
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    
    # Mock cosign signing process
    try:
        # In production: cosign sign --key private.key workflow.wpk.yaml
        new_signature = f"cosign-{hashlib.sha256(workflow_id.encode()).hexdigest()[:16]}"
        
        # Update signature in WPK file
        with open(workflow["file_path"], 'r') as f:
            wpk_data = yaml.safe_load(f)
        
        wpk_data["metadata"]["signature"] = new_signature
        
        with open(workflow["file_path"], 'w') as f:
            yaml.dump(wpk_data, f, default_flow_style=False)
        
        # Update metadata
        workflow["signature"] = new_signature
        workflow["signed_at"] = datetime.utcnow().isoformat()
        workflows[workflow_id] = workflow
        save_workflows(workflows)
        
        return {
            "message": "Workflow signed successfully",
            "signature": new_signature
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signing failed: {str(e)}")

@app.delete("/workflows/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a workflow (admin only)"""
    workflows = load_workflows()
    
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    
    # Remove WPK file
    try:
        os.remove(workflow["file_path"])
    except FileNotFoundError:
        pass
    
    # Remove from registry
    del workflows[workflow_id]
    save_workflows(workflows)
    
    return {"message": "Workflow deleted successfully"}

@app.get("/workflows/{workflow_id}/runs")
async def get_workflow_runs(
    workflow_id: str,
    limit: int = 20,
    page: int = 1
):
    """Get paginated run history for a workflow"""
    try:
        # Import run_logger here to avoid circular imports
        from run_logger import get_runs_by_wpk_id
        
        offset = (page - 1) * limit
        runs = get_runs_by_wpk_id(workflow_id, limit=limit, offset=offset)
        
        # Format runs for API response
        formatted_runs = []
        for run in runs:
            formatted_runs.append({
                "run_id": run[0],
                "status": run[1], 
                "duration_ms": run[2],
                "created_at": run[3]
            })
        
        return {
            "workflow_id": workflow_id,
            "runs": formatted_runs,
            "page": page,
            "limit": limit,
            "total": len(formatted_runs)
        }
        
    except Exception as e:
        logger.error(f"Failed to get runs for workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow runs: {str(e)}")

@app.post("/workflows/{workflow_id}/runs/notify")
async def notify_workflow_run(
    workflow_id: str,
    run_data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Notify registry of new workflow run and update latest_run_id"""
    workflows = load_workflows()
    
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    try:
        # Update workflow metadata with latest run info
        workflow = workflows[workflow_id]
        workflow["latest_run_id"] = run_data.get("run_id")
        workflow["latest_run_status"] = run_data.get("status")
        workflow["latest_run_at"] = datetime.utcnow().isoformat()
        workflow["total_runs"] = workflow.get("total_runs", 0) + 1
        
        workflows[workflow_id] = workflow
        save_workflows(workflows)
        
        logger.info(f"Updated workflow {workflow_id} with run {run_data.get('run_id')}")
        
        return {
            "message": "Workflow run notification processed",
            "workflow_id": workflow_id,
            "run_id": run_data.get("run_id"),
            "status": "updated"
        }
        
    except Exception as e:
        logger.error(f"Failed to notify workflow run: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process run notification: {str(e)}")

@app.post("/workflows/{workflow_id}/dry-run")
async def dry_run_workflow(
    workflow_id: str,
    parameters: Optional[Dict[str, Any]] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Perform dry-run validation and policy check"""
    workflows = load_workflows()
    
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    
    # Load WPK content
    try:
        with open(workflow["file_path"], 'r') as f:
            wpk_content = yaml.safe_load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="WPK file not found")
    
    # Perform static validation
    static_result = static_validator.validate(wpk_content)
    
    # Perform policy evaluation
    policy_result = policy_engine.evaluate(static_result, wpk_content)
    
    # Categorize workflow
    category = policy_engine.categorize_workflow(wpk_content, static_result)
    
    # Generate approval request if needed
    approval_request = None
    if policy_result.approval_required:
        approval_request = policy_engine.generate_approval_request(
            wpk_content, policy_result, "api-user", "Dry-run validation request"
        ).to_dict()
    
    # Format issues for response
    issues = []
    for issue in static_result.issues:
        issues.append({
            "rule_id": issue.rule_id,
            "severity": issue.severity.value,
            "message": issue.message,
            "path": issue.path,
            "suggestion": issue.suggestion,
            "cwe": issue.cwe
        })
    
    return {
        "workflow_id": workflow_id,
        "validation": {
            "valid": static_result.valid,
            "risk_score": static_result.risk_score,
            "issues": issues,
            "policy_decision": policy_result.policy_decision.value,
            "approval_required": policy_result.approval_required,
            "errors": policy_result.errors,
            "warnings": policy_result.warnings
        },
        "category": category,
        "approval_request": approval_request,
        "recommendation": {
            "can_execute": policy_result.can_execute,
            "requires_approval": policy_result.approval_required,
            "safety_mode": wpk_content.get("spec", {}).get("safety", {}).get("mode", "manual")
        },
        "timestamp": datetime.utcnow().isoformat(),
        "dry_run_id": f"dryrun-{workflow_id}-{int(datetime.utcnow().timestamp())}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)