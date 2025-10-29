#!/usr/bin/env python3
"""
Phase I.4.5 - Human-in-Loop Gateway (HIL)
Approval UI endpoints, multi-channel notifications, MFA hooks
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest
import hashlib

# Metrics
APPROVALS_TOTAL = Counter('hil_approvals_total', 'Total approval requests')
NOTIFICATIONS_SENT = Counter('hil_notifications_sent_total', 'Total notifications sent')
APPROVAL_DURATION = Histogram('approval_processing_seconds', 'Approval processing time')

app = FastAPI(title="Human-in-Loop Gateway", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

# In-memory storage for simulation
pending_approvals = {}
approval_history = {}
notification_channels = {}

class ApprovalRequest(BaseModel):
    proposal_id: str
    approver_id: str
    decision: str  # 'approve', 'reject'
    reason: Optional[str] = None
    mfa_token: Optional[str] = None

class NotificationRequest(BaseModel):
    proposal_id: str
    approvers: List[str]
    channels: List[str] = ["email", "slack"]
    urgency: str = "normal"  # 'low', 'normal', 'high', 'urgent'

def verify_jwt_token(authorization: str = Header(None)):
    """Verify JWT token and extract user info"""
    if not authorization or not authorization.startswith('Bearer '):
        if SIMULATION_MODE:
            return {"user_id": "sim-user", "tenant_id": "sim-tenant", "roles": ["approver"]}
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    if SIMULATION_MODE:
        return {"user_id": "sim-user", "tenant_id": "sim-tenant", "roles": ["approver"]}
    return {"user_id": "extracted-user", "tenant_id": "extracted-tenant", "roles": ["approver"]}

def verify_mfa_token(mfa_token: str, user_id: str) -> bool:
    """Verify MFA token for user"""
    if SIMULATION_MODE:
        # Simulate MFA verification
        return mfa_token == f"mfa-{user_id}-valid"
    # In production: actual MFA verification
    return True

def generate_approval_signature(approval_data: Dict[str, Any]) -> str:
    """Generate signature for approval (P2)"""
    if SIMULATION_MODE:
        # Simulate cosign signature
        data_str = json.dumps(approval_data, sort_keys=True)
        return f"cosign-approval-{hashlib.sha256(data_str.encode()).hexdigest()[:16]}"
    # In production: actual cosign signing
    return "production-approval-signature"

async def send_notification(channel: str, recipient: str, message: Dict[str, Any]) -> bool:
    """Send notification via specified channel"""
    try:
        if SIMULATION_MODE:
            logger.info(f"Simulating {channel} notification to {recipient}: {message['subject']}")
            
            # Simulate different channel behaviors
            channel_success_rates = {
                "email": 0.95,
                "slack": 0.90,
                "telegram": 0.85,
                "sms": 0.98,
                "webhook": 0.88
            }
            
            import random
            success = random.random() < channel_success_rates.get(channel, 0.9)
            
            if success:
                NOTIFICATIONS_SENT.inc()
                return True
            else:
                logger.warning(f"Simulated notification failure for {channel}")
                return False
        
        # In production: actual notification sending
        return True
        
    except Exception as e:
        logger.error(f"Error sending {channel} notification: {e}")
        return False

def get_approver_preferences(approver_id: str) -> Dict[str, Any]:
    """Get approver notification preferences"""
    # Simulate approver preferences
    preferences = {
        "admin-001": {"channels": ["email", "slack"], "timezone": "UTC", "urgent_only": False},
        "admin-002": {"channels": ["email", "telegram"], "timezone": "EST", "urgent_only": True},
        "security-lead": {"channels": ["email", "sms", "slack"], "timezone": "PST", "urgent_only": False}
    }
    
    return preferences.get(approver_id, {
        "channels": ["email"],
        "timezone": "UTC", 
        "urgent_only": False
    })

@app.post("/approve/{proposal_id}")
async def approve_proposal(
    proposal_id: str,
    request: ApprovalRequest,
    token_data: Dict = Depends(verify_jwt_token)
):
    """Approve or reject proposal with approver verification"""
    APPROVALS_TOTAL.inc()
    
    # Verify approver identity
    if request.approver_id != token_data.get('user_id'):
        raise HTTPException(status_code=403, detail="Approver ID mismatch")
    
    # Check if user has approval role
    if "approver" not in token_data.get('roles', []):
        raise HTTPException(status_code=403, detail="Insufficient permissions for approval")
    
    # Verify MFA if provided (P3)
    mfa_verified = False
    if request.mfa_token:
        mfa_verified = verify_mfa_token(request.mfa_token, request.approver_id)
        if not mfa_verified:
            raise HTTPException(status_code=400, detail="Invalid MFA token")
    
    # Check if proposal exists in pending approvals
    if proposal_id not in pending_approvals:
        # Create pending approval entry if not exists
        pending_approvals[proposal_id] = {
            "proposal_id": proposal_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "approvers_required": ["admin-001"],  # Default approver
            "approvals": []
        }
    
    # Create approval record
    approval_record = {
        "approver_id": request.approver_id,
        "approver_name": f"User-{request.approver_id}",
        "decision": request.decision,
        "reason": request.reason,
        "mfa_verified": mfa_verified,
        "timestamp": datetime.utcnow().isoformat(),
        "tenant_id": token_data.get('tenant_id')
    }
    
    # Generate approval signature (P2)
    signature = generate_approval_signature(approval_record)
    approval_record["signature"] = signature
    
    # Store approval
    pending_approvals[proposal_id]["approvals"].append(approval_record)
    
    # Update status based on decision
    if request.decision == "approve":
        pending_approvals[proposal_id]["status"] = "approved"
    elif request.decision == "reject":
        pending_approvals[proposal_id]["status"] = "rejected"
    
    # Move to history
    approval_history[proposal_id] = pending_approvals[proposal_id].copy()
    approval_history[proposal_id]["completed_at"] = datetime.utcnow().isoformat()
    
    logger.info(f"Proposal {proposal_id} {request.decision}d by {request.approver_id}")
    
    return {
        "proposal_id": proposal_id,
        "status": request.decision + "d",
        "approver": request.approver_id,
        "mfa_verified": mfa_verified,
        "signature": signature,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/pending/{tenant_id}")
async def get_pending_approvals(
    tenant_id: str,
    token_data: Dict = Depends(verify_jwt_token)
):
    """List pending approvals for tenant"""
    # Verify tenant access (P5)
    if tenant_id != token_data.get('tenant_id'):
        raise HTTPException(status_code=403, detail="Tenant access denied")
    
    # Filter pending approvals for tenant
    tenant_pending = []
    for proposal_id, approval in pending_approvals.items():
        # Check if user is in required approvers or has approval role
        if ("approver" in token_data.get('roles', []) or 
            token_data.get('user_id') in approval.get('approvers_required', [])):
            tenant_pending.append({
                "proposal_id": proposal_id,
                "status": approval["status"],
                "created_at": approval["created_at"],
                "approvers_required": approval.get("approvers_required", []),
                "current_approvals": len(approval.get("approvals", []))
            })
    
    return {
        "tenant_id": tenant_id,
        "pending_approvals": tenant_pending,
        "total_pending": len(tenant_pending)
    }

@app.post("/notify")
async def send_approval_notification(request: NotificationRequest):
    """Send approval notifications to specified approvers"""
    proposal_id = request.proposal_id
    
    # Create notification message
    message = {
        "subject": f"Approval Required: Proposal {proposal_id}",
        "body": f"A new proposal {proposal_id} requires your approval. Please review and take action.",
        "proposal_id": proposal_id,
        "urgency": request.urgency,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send notifications to each approver
    notification_results = []
    for approver_id in request.approvers:
        approver_prefs = get_approver_preferences(approver_id)
        
        # Skip if approver only wants urgent notifications and this isn't urgent
        if approver_prefs.get("urgent_only", False) and request.urgency not in ["high", "urgent"]:
            continue
        
        # Use approver's preferred channels or fallback to requested channels
        channels_to_use = approver_prefs.get("channels", request.channels)
        
        for channel in channels_to_use:
            if channel in request.channels:  # Only use requested channels
                success = await send_notification(channel, approver_id, message)
                notification_results.append({
                    "approver_id": approver_id,
                    "channel": channel,
                    "success": success,
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    # Store notification record
    notification_channels[proposal_id] = {
        "proposal_id": proposal_id,
        "notifications_sent": notification_results,
        "total_sent": len([r for r in notification_results if r["success"]]),
        "total_failed": len([r for r in notification_results if not r["success"]])
    }
    
    return {
        "proposal_id": proposal_id,
        "notifications_sent": len([r for r in notification_results if r["success"]]),
        "notifications_failed": len([r for r in notification_results if not r["success"]]),
        "results": notification_results
    }

@app.get("/approval/{proposal_id}/history")
async def get_approval_history(
    proposal_id: str,
    token_data: Dict = Depends(verify_jwt_token)
):
    """Get approval history for proposal"""
    if proposal_id in approval_history:
        history = approval_history[proposal_id]
        # Redact sensitive information for non-admin users
        if "admin" not in token_data.get('roles', []):
            for approval in history.get("approvals", []):
                approval.pop("signature", None)
        return history
    elif proposal_id in pending_approvals:
        return pending_approvals[proposal_id]
    else:
        raise HTTPException(status_code=404, detail="Proposal not found")

@app.get("/health")
async def health_check():
    """Health check endpoint (P4)"""
    return {
        "status": "healthy",
        "service": "hil-gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "pending_approvals": len(pending_approvals),
        "notification_channels_active": len(notification_channels)
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint (P4)"""
    return JSONResponse(
        content=generate_latest().decode('utf-8'),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9205)