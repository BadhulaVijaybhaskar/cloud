#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="CI Runner")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class BuildRequest(BaseModel):
    repo: str
    ref: str
    tenant_id: str = "default"

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "h5-ci-runner", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {"builds_total": 234, "test_runs": 189, "artifacts_published": 156, "simulation": SIMULATION_MODE}

@app.post("/ci/build")
async def trigger_build(req: BuildRequest):
    if SIMULATION_MODE:
        build_id = f"build-{hash(req.repo + req.ref) % 10000}"
        
        build_result = {
            "build_id": build_id,
            "repo": req.repo,
            "ref": req.ref,
            "tenant_id": req.tenant_id,
            "status": "success",
            "steps": {
                "checkout": {"status": "success", "duration": "15s"},
                "test": {"status": "success", "duration": "2m30s", "tests_passed": 47},
                "build": {"status": "success", "duration": "1m45s"},
                "push": {"status": "success", "duration": "30s", "image": f"registry.local/{req.tenant_id}/app:latest"}
            },
            "manifest_signed": True,
            "cosign_signature": "<REDACTED>",
            "policy_validation": "passed",
            "simulation": True
        }
        
        logger.info(f"Build completed: {build_id} for {req.repo}@{req.ref}")
        return build_result
    
    return {"status": "error", "message": "CI infrastructure required"}

@app.post("/ci/deploy")
async def deploy_manifest(deploy_data: dict):
    if SIMULATION_MODE:
        manifest_id = deploy_data.get("manifest_id", "manifest-sim")
        namespace = deploy_data.get("namespace", "default")
        
        deploy_result = {
            "manifest_id": manifest_id,
            "namespace": namespace,
            "status": "deployed",
            "resources_created": ["deployment", "service", "configmap"],
            "replicas": 3,
            "health_check": "passed",
            "simulation": True
        }
        
        return deploy_result
    
    return {"status": "error", "message": "Deployment infrastructure required"}

@app.get("/ci/artifacts/{build_id}")
async def get_build_artifacts(build_id: str):
    if SIMULATION_MODE:
        return {
            "build_id": build_id,
            "artifacts": [
                {"type": "container_image", "url": "registry.local/app:latest", "sha256": "abc123"},
                {"type": "helm_chart", "url": "charts.local/app-1.0.0.tgz", "sha256": "def456"},
                {"type": "manifest", "url": "manifests.local/app.yaml", "sha256": "ghi789"}
            ],
            "signatures": {
                "cosign": "<REDACTED>",
                "policy_hash": "sha256:policy123"
            },
            "simulation": True
        }
    
    return {"status": "error", "message": "Artifact storage required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8602)