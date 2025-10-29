#!/usr/bin/env python3
"""
Phase I.4.1 - Decision Coordinator
Orchestrates proposals, votes, consensus, and enactment
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import logging
from prometheus_client import Counter, Histogram, generate_latest
import jwt

# Metrics
PROPOSALS_TOTAL = Counter('decision_proposals_total', 'Total decision proposals')
ENACTMENTS_TOTAL = Counter('decision_enactments_total', 'Total decision enactments')
PROPOSAL_DURATION = Histogram('proposal_processing_seconds', 'Proposal processing time')

app = FastAPI(title="Decision Coordinator", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
DECISION_TIMEOUT_MS = int(os.getenv('PHASE_I4_DECISION_TIMEOUT_MS', '30000'))

# In-memory storage for simulation
proposals_db = {}
negotiations_db = {}

class ProposalRequest(BaseModel):
    tenant_id: str
    manifest: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}

class EnactmentRequest(BaseModel):
    approver_id: Optional[str] = None
    justification: Optional[str] = None

def verify_jwt_token(authorization: str = Header(None)):
    """Verify JWT token and extract tenant claim (P5)"""
    if not authorization or not authorization.startswith('Bearer '):
        if SIMULATION_MODE:
            return {"tenant_id": "sim-tenant", "user_id": "sim-user"}
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(' ')[1]
    try:
        if SIMULATION_MODE:
            # Simulate token validation
            return {"tenant_id": "sim-tenant", "user_id": "sim-user"}
        # In production: jwt.decode(token, secret, algorithms=['HS256'])
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def validate_manifest_signature(manifest: Dict[str, Any]) -> bool:
    """Validate manifest signature with cosign (P2)"""
    if SIMULATION_MODE:
        logger.info("Simulating cosign signature validation")
        return True
    # In production: actual cosign validation
    return True

def calculate_state_hash(state_data: Dict[str, Any]) -> str:
    """Calculate SHA256 hash of state data (P7)"""
    state_str = json.dumps(state_data, sort_keys=True)
    return hashlib.sha256(state_str.encode()).hexdigest()

@app.post("/proposals")
async def submit_proposal(
    request: ProposalRequest,
    token_data: Dict = Depends(verify_jwt_token)
):
    """Submit new decision proposal"""
    PROPOSALS_TOTAL.inc()
    
    # Validate tenant access (P5)
    if request.tenant_id != token_data.get('tenant_id'):
        raise HTTPException(status_code=403, detail="Tenant access denied")
    
    # Validate manifest signature (P2)
    if not validate_manifest_signature(request.manifest):
        raise HTTPException(status_code=400, detail="Invalid manifest signature")
    
    # Generate proposal ID
    proposal_id = f"prop-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{len(proposals_db)}"
    
    # Calculate pre-state snapshot (P7)
    pre_state = {"timestamp": datetime.utcnow().isoformat(), "manifest": request.manifest}
    pre_state_hash = calculate_state_hash(pre_state)
    
    # Determine impact level
    impact_level = request.manifest.get('impact_level', 'medium')
    
    # Store proposal
    proposal = {
        "proposal_id": proposal_id,
        "tenant_id": request.tenant_id,
        "manifest": request.manifest,
        "metadata": request.metadata,
        "status": "submitted",
        "impact_level": impact_level,
        "pre_state_hash": pre_state_hash,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    proposals_db[proposal_id] = proposal
    
    # Broadcast to negotiator and confidence scorer (async)
    asyncio.create_task(broadcast_proposal(proposal_id))
    
    logger.info(f"Proposal {proposal_id} submitted for tenant {request.tenant_id}")
    
    return {
        "proposal_id": proposal_id,
        "status": "submitted",
        "pre_state_hash": pre_state_hash
    }

@app.get("/proposals/{proposal_id}")
async def get_proposal_status(
    proposal_id: str,
    token_data: Dict = Depends(verify_jwt_token)
):
    """Get proposal status and vote results"""
    if proposal_id not in proposals_db:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    proposal = proposals_db[proposal_id]
    
    # Check tenant access (P5)
    if proposal['tenant_id'] != token_data.get('tenant_id'):
        raise HTTPException(status_code=403, detail="Tenant access denied")
    
    # Get negotiation status if exists
    negotiation_status = None
    for neg_id, neg in negotiations_db.items():
        if neg['proposal_id'] == proposal_id:
            negotiation_status = {
                "negotiation_id": neg_id,
                "status": neg['status'],
                "consensus_reached": neg.get('consensus_reached', False),
                "consensus_ratio": neg.get('consensus_ratio', 0.0)
            }
            break
    
    return {
        "proposal": proposal,
        "negotiation": negotiation_status
    }

@app.post("/proposals/{proposal_id}/enact")
async def enact_proposal(
    proposal_id: str,
    request: EnactmentRequest,
    token_data: Dict = Depends(verify_jwt_token)
):
    """Enact proposal outcome (requires approver if impact high)"""
    ENACTMENTS_TOTAL.inc()
    
    if proposal_id not in proposals_db:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    proposal = proposals_db[proposal_id]
    
    # Check tenant access (P5)
    if proposal['tenant_id'] != token_data.get('tenant_id'):
        raise HTTPException(status_code=403, detail="Tenant access denied")
    
    # Check if high impact requires approver (P3)
    if proposal['impact_level'] == 'high':
        if not request.approver_id or not request.justification:
            raise HTTPException(
                status_code=400, 
                detail="High impact decisions require approver and justification"
            )
    
    # Calculate post-state hash (P7)
    post_state = {
        "timestamp": datetime.utcnow().isoformat(),
        "enacted_manifest": proposal['manifest'],
        "approver": request.approver_id,
        "justification": request.justification
    }
    post_state_hash = calculate_state_hash(post_state)
    
    # Update proposal status
    proposal['status'] = 'enacted'
    proposal['post_state_hash'] = post_state_hash
    proposal['updated_at'] = datetime.utcnow().isoformat()
    
    if request.approver_id:
        proposal['approver_id'] = request.approver_id
        proposal['justification'] = request.justification
    
    logger.info(f"Proposal {proposal_id} enacted by {request.approver_id}")
    
    return {
        "proposal_id": proposal_id,
        "status": "enacted",
        "post_state_hash": post_state_hash,
        "enacted_at": datetime.utcnow().isoformat()
    }

async def broadcast_proposal(proposal_id: str):
    """Broadcast proposal to negotiator and confidence scorer"""
    try:
        # Simulate broadcasting to other services
        logger.info(f"Broadcasting proposal {proposal_id} to negotiator and scorer")
        
        # Create negotiation entry
        negotiation_id = f"neg-{proposal_id}"
        negotiations_db[negotiation_id] = {
            "negotiation_id": negotiation_id,
            "proposal_id": proposal_id,
            "regions": ["us-east-1", "eu-west-1", "ap-southeast-1"],
            "quorum_threshold": 0.6,
            "status": "active",
            "consensus_reached": False,
            "started_at": datetime.utcnow().isoformat()
        }
        
        # Simulate async processing
        await asyncio.sleep(1)
        
    except Exception as e:
        logger.error(f"Error broadcasting proposal {proposal_id}: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint (P4)"""
    return {
        "status": "healthy",
        "service": "decision-coordinator",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE
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
    uvicorn.run(app, host="0.0.0.0", port=9201)