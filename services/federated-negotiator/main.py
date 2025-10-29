#!/usr/bin/env python3
"""
Phase I.4.3 - Federated Negotiator
Multi-region agent negotiation engine with consensus algorithms
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
NEGOTIATIONS_TOTAL = Counter('negotiations_total', 'Total negotiations started')
CONSENSUS_REACHED = Counter('consensus_reached_total', 'Total consensus reached')
NEGOTIATION_DURATION = Histogram('negotiation_duration_seconds', 'Negotiation duration')

app = FastAPI(title="Federated Negotiator", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
DECISION_TIMEOUT_MS = int(os.getenv('PHASE_I4_DECISION_TIMEOUT_MS', '30000'))

# In-memory storage for simulation
negotiations_db = {}
regional_votes_db = {}

class NegotiationRequest(BaseModel):
    proposal_id: str
    regions: Optional[List[str]] = ["us-east-1", "eu-west-1", "ap-southeast-1"]
    quorum_threshold: Optional[float] = 0.6
    timeout_minutes: Optional[int] = 30

class RegionalVote(BaseModel):
    region: str
    vote: str  # 'approve', 'reject', 'abstain'
    weight: Optional[float] = 1.0
    reasoning: Optional[str] = None

def simulate_regional_agent_vote(region: str, proposal_id: str) -> Dict[str, Any]:
    """Simulate regional agent voting decision"""
    # Simulate different regional preferences
    regional_preferences = {
        "us-east-1": {"approve_bias": 0.7, "latency": 1.0},
        "eu-west-1": {"approve_bias": 0.6, "latency": 1.5}, 
        "ap-southeast-1": {"approve_bias": 0.8, "latency": 2.0},
        "us-west-2": {"approve_bias": 0.65, "latency": 1.2},
        "eu-central-1": {"approve_bias": 0.55, "latency": 1.8}
    }
    
    prefs = regional_preferences.get(region, {"approve_bias": 0.6, "latency": 1.0})
    
    # Simulate decision based on bias
    import random
    vote_decision = "approve" if random.random() < prefs["approve_bias"] else "reject"
    
    return {
        "vote": vote_decision,
        "weight": 1.0,
        "reasoning": f"Regional policy evaluation for {region}",
        "response_time": prefs["latency"]
    }

async def conduct_regional_voting(negotiation_id: str, regions: List[str]):
    """Conduct voting across regions with simulated latency"""
    try:
        negotiation = negotiations_db[negotiation_id]
        proposal_id = negotiation["proposal_id"]
        
        # Simulate parallel voting with different latencies
        vote_tasks = []
        for region in regions:
            vote_tasks.append(simulate_regional_vote_async(region, proposal_id, negotiation_id))
        
        # Wait for all votes with timeout
        timeout_seconds = DECISION_TIMEOUT_MS / 1000
        try:
            await asyncio.wait_for(asyncio.gather(*vote_tasks), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            logger.warning(f"Negotiation {negotiation_id} timed out")
            negotiation["status"] = "timeout"
            return
        
        # Calculate consensus
        consensus_result = calculate_consensus(negotiation_id)
        negotiation["consensus_reached"] = consensus_result["consensus_reached"]
        negotiation["consensus_ratio"] = consensus_result["consensus_ratio"]
        
        if consensus_result["consensus_reached"]:
            negotiation["status"] = "consensus_reached"
            CONSENSUS_REACHED.inc()
            logger.info(f"Consensus reached for negotiation {negotiation_id}")
        else:
            negotiation["status"] = "consensus_failed"
            logger.info(f"Consensus failed for negotiation {negotiation_id}")
        
        negotiation["completed_at"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        logger.error(f"Error in regional voting for {negotiation_id}: {e}")
        negotiation["status"] = "error"
        negotiation["error"] = str(e)

async def simulate_regional_vote_async(region: str, proposal_id: str, negotiation_id: str):
    """Simulate async regional vote with latency"""
    vote_result = simulate_regional_agent_vote(region, proposal_id)
    
    # Simulate network latency
    await asyncio.sleep(vote_result["response_time"])
    
    # Store vote
    vote_id = f"{negotiation_id}-{region}"
    regional_votes_db[vote_id] = {
        "negotiation_id": negotiation_id,
        "region": region,
        "vote": vote_result["vote"],
        "weight": vote_result["weight"],
        "reasoning": vote_result["reasoning"],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Region {region} voted {vote_result['vote']} for negotiation {negotiation_id}")

def calculate_consensus(negotiation_id: str) -> Dict[str, Any]:
    """Calculate consensus based on regional votes"""
    negotiation = negotiations_db[negotiation_id]
    threshold = negotiation["quorum_threshold"]
    
    # Get all votes for this negotiation
    votes = [v for v in regional_votes_db.values() if v["negotiation_id"] == negotiation_id]
    
    if not votes:
        return {"consensus_ratio": 0.0, "consensus_reached": False}
    
    # Calculate weighted consensus
    total_weight = sum(v["weight"] for v in votes)
    approve_weight = sum(v["weight"] for v in votes if v["vote"] == "approve")
    
    consensus_ratio = approve_weight / total_weight if total_weight > 0 else 0.0
    consensus_reached = consensus_ratio >= threshold
    
    return {
        "consensus_ratio": round(consensus_ratio, 3),
        "consensus_reached": consensus_reached,
        "total_votes": len(votes),
        "approve_votes": len([v for v in votes if v["vote"] == "approve"]),
        "reject_votes": len([v for v in votes if v["vote"] == "reject"])
    }

@app.post("/negotiate")
async def start_negotiation(
    request: NegotiationRequest,
    background_tasks: BackgroundTasks
):
    """Start negotiation across regions"""
    NEGOTIATIONS_TOTAL.inc()
    
    # Generate negotiation ID
    negotiation_id = f"neg-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{len(negotiations_db)}"
    
    # Calculate timeout
    timeout_at = datetime.utcnow() + timedelta(minutes=request.timeout_minutes)
    
    # Store negotiation
    negotiation = {
        "negotiation_id": negotiation_id,
        "proposal_id": request.proposal_id,
        "regions": request.regions,
        "quorum_threshold": request.quorum_threshold,
        "status": "active",
        "consensus_reached": False,
        "consensus_ratio": 0.0,
        "started_at": datetime.utcnow().isoformat(),
        "timeout_at": timeout_at.isoformat()
    }
    
    negotiations_db[negotiation_id] = negotiation
    
    # Start background voting process
    background_tasks.add_task(conduct_regional_voting, negotiation_id, request.regions)
    
    logger.info(f"Started negotiation {negotiation_id} for proposal {request.proposal_id}")
    
    return {
        "negotiation_id": negotiation_id,
        "status": "active",
        "regions": request.regions,
        "quorum_threshold": request.quorum_threshold,
        "timeout_at": timeout_at.isoformat()
    }

@app.get("/negotiate/{negotiation_id}/status")
async def get_negotiation_status(negotiation_id: str):
    """Get negotiation progress and results"""
    if negotiation_id not in negotiations_db:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    
    negotiation = negotiations_db[negotiation_id]
    
    # Get votes for this negotiation
    votes = [v for v in regional_votes_db.values() if v["negotiation_id"] == negotiation_id]
    
    # Calculate current consensus if active
    consensus_info = {}
    if negotiation["status"] in ["active", "consensus_reached", "consensus_failed"]:
        consensus_info = calculate_consensus(negotiation_id)
    
    return {
        "negotiation": negotiation,
        "votes": votes,
        "consensus_info": consensus_info,
        "progress": {
            "total_regions": len(negotiation["regions"]),
            "votes_received": len(votes),
            "completion_percentage": round((len(votes) / len(negotiation["regions"])) * 100, 1)
        }
    }

@app.post("/negotiate/{negotiation_id}/vote")
async def submit_regional_vote(
    negotiation_id: str,
    vote: RegionalVote
):
    """Submit vote from regional agent (for manual testing)"""
    if negotiation_id not in negotiations_db:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    
    negotiation = negotiations_db[negotiation_id]
    
    if negotiation["status"] != "active":
        raise HTTPException(status_code=400, detail="Negotiation not active")
    
    # Store vote
    vote_id = f"{negotiation_id}-{vote.region}"
    regional_votes_db[vote_id] = {
        "negotiation_id": negotiation_id,
        "region": vote.region,
        "vote": vote.vote,
        "weight": vote.weight,
        "reasoning": vote.reasoning,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Check if all regions have voted
    votes = [v for v in regional_votes_db.values() if v["negotiation_id"] == negotiation_id]
    if len(votes) >= len(negotiation["regions"]):
        # Calculate final consensus
        consensus_result = calculate_consensus(negotiation_id)
        negotiation["consensus_reached"] = consensus_result["consensus_reached"]
        negotiation["consensus_ratio"] = consensus_result["consensus_ratio"]
        negotiation["status"] = "consensus_reached" if consensus_result["consensus_reached"] else "consensus_failed"
        negotiation["completed_at"] = datetime.utcnow().isoformat()
    
    return {"status": "vote_recorded", "negotiation_status": negotiation["status"]}

@app.get("/health")
async def health_check():
    """Health check endpoint (P4)"""
    return {
        "status": "healthy",
        "service": "federated-negotiator",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "active_negotiations": len([n for n in negotiations_db.values() if n["status"] == "active"])
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
    uvicorn.run(app, host="0.0.0.0", port=9203)