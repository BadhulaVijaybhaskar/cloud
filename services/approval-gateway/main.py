#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Approval Gateway")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class ApprovalRequest(BaseModel):
    exec_id: str
    approver: str
    action_type: str = "unknown"
    urgency: str = "normal"

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "approval-gateway", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {"approval_requests": 67, "approvals_granted": 45, "approvals_denied": 12, "simulation": SIMULATION_MODE}

@app.post("/request_approval")
async def request_approval(req: ApprovalRequest):
    if SIMULATION_MODE:
        # Simulate approval request
        approval_id = f"appr-{hash(req.exec_id) % 10000}"
        
        # Simulate notification sending
        notification_result = {
            "approval_id": approval_id,
            "exec_id": req.exec_id,
            "approver": req.approver,
            "notification_sent": True,
            "channels": ["email", "slack"],
            "ttl_minutes": 30 if req.urgency == "high" else 60,
            "simulation": True
        }
        
        logger.info(f"Approval request sent: {approval_id} to {req.approver}")
        return notification_result
    
    return {"status": "error", "message": "Notification infrastructure required"}

@app.post("/approve")
async def approve_action(approval_data: dict):
    if SIMULATION_MODE:
        approval_id = approval_data.get("approval_id")
        approver_token = approval_data.get("token", "<REDACTED>")
        
        result = {
            "approval_id": approval_id,
            "status": "approved",
            "approver": "admin@example.com",
            "timestamp": "2024-01-15T10:30:00Z",
            "mfa_verified": True,
            "approval_token": "<REDACTED>",
            "simulation": True
        }
        
        logger.info(f"Action approved: {approval_id}")
        return result
    
    return {"status": "error", "message": "Approval processing required"}

@app.get("/pending/{approver}")
async def get_pending_approvals(approver: str):
    if SIMULATION_MODE:
        return {
            "approver": approver,
            "pending": [
                {"id": "appr-1234", "action": "scale_up", "tenant": "tenant-1", "urgency": "normal"},
                {"id": "appr-5678", "action": "rotate_keys", "tenant": "tenant-2", "urgency": "high"}
            ],
            "count": 2,
            "simulation": True
        }
    
    return {"status": "error", "message": "Approval storage required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8806)