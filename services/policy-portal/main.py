#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI

app = FastAPI(title="Policy Portal API")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "policy-portal", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {"portal_queries_total": 234, "dashboard_views": 45, "simulation": SIMULATION_MODE}

@app.get("/portal/dashboard")
async def get_dashboard():
    if SIMULATION_MODE:
        return {
            "hub_status": "active",
            "edge_nodes": 5,
            "policies_active": 12,
            "sync_health": "good",
            "last_audit": "2024-01-15T10:30:00Z",
            "compliance_score": 100,
            "simulation": True
        }
    
    return {"status": "error", "message": "Portal backend required"}

@app.get("/portal/sync-status")
async def get_sync_status():
    if SIMULATION_MODE:
        return {
            "global_sync_state": "consistent",
            "edge_nodes": [
                {"id": "edge-001", "status": "synced", "last_sync": "2024-01-15T10:29:45Z"},
                {"id": "edge-002", "status": "synced", "last_sync": "2024-01-15T10:29:50Z"},
                {"id": "edge-003", "status": "synced", "last_sync": "2024-01-15T10:29:48Z"}
            ],
            "policies_in_sync": 12,
            "simulation": True
        }
    
    return {"status": "error", "message": "Sync monitoring required"}

@app.get("/portal/audit-results")
async def get_audit_results():
    if SIMULATION_MODE:
        try:
            with open("reports/edge_audit_summary.json", "r") as f:
                audit_data = json.load(f)
                return {
                    "latest_audit": audit_data,
                    "compliance_trend": "stable",
                    "violations_last_30d": 0,
                    "simulation": True
                }
        except FileNotFoundError:
            return {
                "latest_audit": None,
                "compliance_trend": "unknown",
                "violations_last_30d": 0,
                "simulation": True
            }
    
    return {"status": "error", "message": "Audit storage required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8705)