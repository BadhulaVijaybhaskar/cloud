#!/usr/bin/env python3
"""
AOL UI Proxy - UI API for LaunchPad integration
Phase I.6.6 - UI Proxy implementation
"""

import os
import json
import requests
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from prometheus_client import Counter, generate_latest

# Metrics
ui_requests = Counter('aol_ui_requests_total', 'Total UI API requests', ['endpoint'])
proxy_errors = Counter('aol_ui_proxy_errors_total', 'Total proxy errors')

# Models
class ApprovalRequest(BaseModel):
    approver: str
    comment: Optional[str] = None

app = FastAPI(title="AOL UI Proxy", version="1.0.0")

# Configuration
AOL_CONTROLLER_URL = os.getenv("AOL_CONTROLLER_URL", "http://localhost:8601")
simulation_mode = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "aol-ui-proxy",
        "simulation_mode": simulation_mode,
        "aol_controller_url": AOL_CONTROLLER_URL
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.get("/v1/ui/proposals")
async def list_proposals():
    """List optimization proposals for UI"""
    ui_requests.labels(endpoint="list_proposals").inc()
    
    if simulation_mode:
        # Return simulated proposals
        return {
            "proposals": [
                {
                    "id": "prop_001",
                    "scope": "tenant:demo",
                    "status": "proposed",
                    "risk_level": "low",
                    "created_at": "2024-12-19T10:30:00Z",
                    "summary": "CPU optimization for demo tenant"
                },
                {
                    "id": "prop_002", 
                    "scope": "global",
                    "status": "simulated",
                    "risk_level": "medium",
                    "created_at": "2024-12-19T10:25:00Z",
                    "summary": "Router timeout optimization"
                }
            ],
            "total": 2,
            "simulation_mode": True
        }
    
    # In production: proxy to AOL controller
    try:
        # Would make actual request to AOL controller
        return {"proposals": [], "total": 0, "note": "Production proxy not implemented"}
    except Exception as e:
        proxy_errors.inc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch proposals: {str(e)}")

@app.get("/v1/ui/proposals/{proposal_id}")
async def get_proposal_details(proposal_id: str):
    """Get detailed proposal information for UI"""
    ui_requests.labels(endpoint="get_proposal").inc()
    
    if simulation_mode:
        # Return simulated proposal details
        return {
            "id": proposal_id,
            "scope": "tenant:demo",
            "status": "proposed",
            "risk_level": "low",
            "created_at": "2024-12-19T10:30:00Z",
            "changes": [
                {
                    "path": "scheduler.cpu_limit",
                    "current_value": 1.0,
                    "suggested_value": 1.2,
                    "reason": "CPU utilization 85% exceeds target 60%"
                }
            ],
            "explanation": {
                "overall_rationale": "This optimization addresses CPU utilization issues in demo tenant",
                "risk_explanation": {
                    "level": "low",
                    "description": "Minimal risk - small parameter adjustment within safe bounds"
                },
                "expected_impact": "5-10% performance improvement"
            },
            "simulation_mode": True
        }
    
    # In production: proxy to AOL controller
    try:
        response = requests.get(f"{AOL_CONTROLLER_URL}/v1/proposals/{proposal_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Proposal not found")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        proxy_errors.inc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch proposal: {str(e)}")

@app.post("/v1/ui/proposals/{proposal_id}/simulate")
async def simulate_proposal_ui(proposal_id: str):
    """Trigger proposal simulation from UI"""
    ui_requests.labels(endpoint="simulate_proposal").inc()
    
    if simulation_mode:
        return {
            "proposal_id": proposal_id,
            "status": "simulation_started",
            "estimated_duration": "2-3 minutes",
            "simulation_mode": True
        }
    
    # In production: proxy to AOL controller
    try:
        response = requests.post(f"{AOL_CONTROLLER_URL}/v1/proposals/{proposal_id}/simulate", json={})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        proxy_errors.inc()
        raise HTTPException(status_code=500, detail=f"Failed to start simulation: {str(e)}")

@app.post("/v1/ui/proposals/{proposal_id}/approve")
async def approve_proposal(proposal_id: str, request: ApprovalRequest):
    """Approve and apply proposal from UI"""
    ui_requests.labels(endpoint="approve_proposal").inc()
    
    if simulation_mode:
        return {
            "proposal_id": proposal_id,
            "status": "approved_and_applied",
            "approver": request.approver,
            "comment": request.comment,
            "applied_at": "2024-12-19T10:35:00Z",
            "simulation_mode": True
        }
    
    # In production: proxy to AOL controller apply endpoint
    try:
        apply_request = {
            "dry_run": False,
            "approver": request.approver
        }
        response = requests.post(f"{AOL_CONTROLLER_URL}/v1/proposals/{proposal_id}/apply", json=apply_request)
        response.raise_for_status()
        
        result = response.json()
        result["comment"] = request.comment  # Add UI comment
        return result
        
    except requests.RequestException as e:
        proxy_errors.inc()
        raise HTTPException(status_code=500, detail=f"Failed to apply proposal: {str(e)}")

@app.post("/v1/ui/proposals/{proposal_id}/reject")
async def reject_proposal(proposal_id: str, request: ApprovalRequest):
    """Reject proposal from UI"""
    ui_requests.labels(endpoint="reject_proposal").inc()
    
    return {
        "proposal_id": proposal_id,
        "status": "rejected",
        "rejected_by": request.approver,
        "reason": request.comment or "Rejected via UI",
        "rejected_at": "2024-12-19T10:35:00Z",
        "simulation_mode": simulation_mode
    }

@app.get("/v1/ui/dashboard")
async def get_dashboard_data():
    """Get dashboard data for AOL UI"""
    ui_requests.labels(endpoint="dashboard").inc()
    
    if simulation_mode:
        return {
            "summary": {
                "active_proposals": 2,
                "pending_approval": 1,
                "applied_today": 5,
                "success_rate": 0.94
            },
            "recent_optimizations": [
                {
                    "id": "opt_001",
                    "type": "CPU Optimization",
                    "scope": "tenant:demo",
                    "improvement": "12% latency reduction",
                    "applied_at": "2024-12-19T09:30:00Z"
                },
                {
                    "id": "opt_002",
                    "type": "Memory Optimization", 
                    "scope": "global",
                    "improvement": "8% memory efficiency",
                    "applied_at": "2024-12-19T08:45:00Z"
                }
            ],
            "metrics": {
                "avg_cpu_utilization": 0.62,
                "avg_memory_utilization": 0.71,
                "p95_latency": 165.2,
                "error_rate": 0.008
            },
            "simulation_mode": True
        }
    
    # In production: aggregate data from multiple sources
    return {
        "summary": {"note": "Production dashboard not implemented"},
        "simulation_mode": False
    }

@app.get("/v1/ui/metrics")
async def get_optimization_metrics():
    """Get optimization metrics for UI charts"""
    ui_requests.labels(endpoint="metrics").inc()
    
    if simulation_mode:
        # Generate simulated time series data
        import time
        base_time = int(time.time()) - 3600  # Last hour
        
        metrics = {
            "cpu_utilization": [],
            "memory_utilization": [],
            "latency_p95": [],
            "throughput": []
        }
        
        for i in range(12):  # 5-minute intervals
            timestamp = base_time + (i * 300)
            metrics["cpu_utilization"].append({"timestamp": timestamp, "value": 0.6 + (i * 0.02)})
            metrics["memory_utilization"].append({"timestamp": timestamp, "value": 0.7 + (i * 0.01)})
            metrics["latency_p95"].append({"timestamp": timestamp, "value": 180 - (i * 2)})
            metrics["throughput"].append({"timestamp": timestamp, "value": 1200 + (i * 10)})
        
        return {
            "metrics": metrics,
            "time_range": {"start": base_time, "end": base_time + 3600},
            "simulation_mode": True
        }
    
    # In production: query Prometheus for actual metrics
    return {"metrics": {}, "note": "Production metrics not implemented"}

if __name__ == "__main__":
    port = int(os.getenv("AOL_UI_PORT", "8602"))
    uvicorn.run(app, host="0.0.0.0", port=port)