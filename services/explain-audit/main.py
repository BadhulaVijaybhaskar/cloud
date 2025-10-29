#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI

app = FastAPI(title="Explainability & Audit")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "explain-audit", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {"audit_entries": 456, "explanations_generated": 234, "simulation": SIMULATION_MODE}

@app.get("/audit/{audit_id}")
async def get_audit_entry(audit_id: str):
    if SIMULATION_MODE:
        audit_entry = {
            "audit_id": audit_id,
            "timestamp": "2024-01-15T10:30:00Z",
            "action": "scale_up",
            "tenant_id": "tenant-123",
            "justification": "High CPU utilization (85%) detected for 5 minutes. Auto-scaling policy triggered to maintain SLA.",
            "decision_factors": [
                "CPU > 80% threshold",
                "Memory usage stable at 60%",
                "Historical pattern suggests sustained load"
            ],
            "risk_assessment": "Low risk - standard scaling operation",
            "approver": "system-auto" if audit_id.startswith("auto") else "admin@example.com",
            "audit_hash": f"sha256:{hash(audit_id) % 100000}",
            "pqc_signature": "<REDACTED>",
            "simulation": True
        }
        
        logger.info(f"Audit entry retrieved: {audit_id}")
        return audit_entry
    
    return {"status": "error", "message": "Audit storage required"}

@app.post("/explain")
async def generate_explanation(action_data: dict):
    if SIMULATION_MODE:
        action = action_data.get("action", "unknown")
        context = action_data.get("context", {})
        
        explanation = {
            "action": action,
            "human_readable": f"The system decided to {action} because the risk analysis indicated immediate attention was needed.",
            "technical_details": {
                "algorithm": "policy_reasoner_v2",
                "confidence": 0.87,
                "factors_considered": ["resource_metrics", "historical_patterns", "tenant_policies"]
            },
            "alternatives_considered": [
                "monitor_only - rejected due to high risk score",
                "manual_intervention - rejected due to automation policy"
            ],
            "simulation": True
        }
        
        return explanation
    
    return {"status": "error", "message": "Explanation engine required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8805)