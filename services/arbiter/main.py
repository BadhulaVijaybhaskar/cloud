#!/usr/bin/env python3
"""
Phase I.5 - Arbiter
Resolves conflicts between agents using deterministic rules and ML models
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
CONFLICTS_RESOLVED = Counter('conflicts_resolved_total', 'Total conflicts resolved', ['resolution_method'])
ARBITRATION_DURATION = Histogram('arbitration_duration_seconds', 'Arbitration processing time')
RESOLUTION_CONFIDENCE = Histogram('resolution_confidence', 'Confidence scores of resolutions')

app = FastAPI(title="Arbiter", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

# In-memory storage for simulation
conflicts = {}
decisions = {}
arbitration_rules = {}

class ConflictSet(BaseModel):
    conflict_id: str
    agents: List[str]
    positions: Dict[str, Any]  # agent_id -> position
    context: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}

class ArbitrationRequest(BaseModel):
    conflict_set: ConflictSet
    resolution_method: Optional[str] = "auto"  # auto, rules, ml, human
    priority: Optional[str] = "normal"  # low, normal, high, urgent

class DecisionRecord(BaseModel):
    decision_id: str
    conflict_id: str
    resolution: Dict[str, Any]
    confidence: float
    method: str
    rationale: str
    timestamp: str
    metadata: Dict[str, Any]

def load_arbitration_rules() -> Dict[str, Any]:
    """Load arbitration rules"""
    return {
        "resource_conflicts": {
            "rule": "highest_priority_wins",
            "description": "Agent with highest priority gets resource"
        },
        "policy_conflicts": {
            "rule": "most_restrictive_wins", 
            "description": "Most restrictive policy takes precedence"
        },
        "performance_conflicts": {
            "rule": "weighted_average",
            "description": "Use weighted average of agent recommendations"
        },
        "security_conflicts": {
            "rule": "security_first",
            "description": "Security considerations override performance"
        },
        "cost_conflicts": {
            "rule": "cost_benefit_analysis",
            "description": "Choose option with best cost-benefit ratio"
        }
    }

def classify_conflict(conflict_set: ConflictSet) -> str:
    """Classify conflict type based on context and positions"""
    context = conflict_set.context
    positions = conflict_set.positions
    
    # Check context for conflict type indicators
    if "resource" in str(context).lower():
        return "resource_conflicts"
    elif "policy" in str(context).lower():
        return "policy_conflicts"
    elif "performance" in str(context).lower():
        return "performance_conflicts"
    elif "security" in str(context).lower():
        return "security_conflicts"
    elif "cost" in str(context).lower():
        return "cost_conflicts"
    
    # Analyze positions for patterns
    position_types = set()
    for agent_id, position in positions.items():
        if isinstance(position, dict):
            if "priority" in position:
                position_types.add("resource")
            elif "policy_level" in position:
                position_types.add("policy")
            elif "performance_target" in position:
                position_types.add("performance")
    
    if "resource" in position_types:
        return "resource_conflicts"
    elif "policy" in position_types:
        return "policy_conflicts"
    elif "performance" in position_types:
        return "performance_conflicts"
    
    return "general_conflicts"

def apply_rule_based_resolution(conflict_set: ConflictSet, conflict_type: str) -> Dict[str, Any]:
    """Apply rule-based conflict resolution"""
    rules = load_arbitration_rules()
    rule_config = rules.get(conflict_type, rules["resource_conflicts"])
    
    positions = conflict_set.positions
    resolution = {"method": "rule_based", "rule": rule_config["rule"]}
    
    if rule_config["rule"] == "highest_priority_wins":
        # Find agent with highest priority
        max_priority = -1
        winner = None
        for agent_id, position in positions.items():
            priority = position.get("priority", 0) if isinstance(position, dict) else 0
            if priority > max_priority:
                max_priority = priority
                winner = agent_id
        
        resolution.update({
            "winner": winner,
            "winning_position": positions.get(winner),
            "rationale": f"Agent {winner} has highest priority ({max_priority})"
        })
    
    elif rule_config["rule"] == "most_restrictive_wins":
        # Find most restrictive policy
        max_restriction = 0
        winner = None
        for agent_id, position in positions.items():
            restriction = position.get("restriction_level", 0) if isinstance(position, dict) else 0
            if restriction > max_restriction:
                max_restriction = restriction
                winner = agent_id
        
        resolution.update({
            "winner": winner,
            "winning_position": positions.get(winner),
            "rationale": f"Agent {winner} has most restrictive policy (level {max_restriction})"
        })
    
    elif rule_config["rule"] == "weighted_average":
        # Calculate weighted average
        total_weight = 0
        weighted_sum = 0
        for agent_id, position in positions.items():
            if isinstance(position, dict) and "value" in position and "weight" in position:
                weighted_sum += position["value"] * position["weight"]
                total_weight += position["weight"]
        
        avg_value = weighted_sum / total_weight if total_weight > 0 else 0
        resolution.update({
            "result": avg_value,
            "rationale": f"Weighted average of agent positions: {avg_value:.2f}"
        })
    
    elif rule_config["rule"] == "security_first":
        # Find most secure option
        max_security = 0
        winner = None
        for agent_id, position in positions.items():
            security = position.get("security_score", 0) if isinstance(position, dict) else 0
            if security > max_security:
                max_security = security
                winner = agent_id
        
        resolution.update({
            "winner": winner,
            "winning_position": positions.get(winner),
            "rationale": f"Agent {winner} provides highest security (score {max_security})"
        })
    
    else:
        # Default: first agent wins
        winner = list(positions.keys())[0] if positions else None
        resolution.update({
            "winner": winner,
            "winning_position": positions.get(winner) if winner else None,
            "rationale": "Default resolution: first agent position"
        })
    
    return resolution

def apply_ml_resolution(conflict_set: ConflictSet) -> Dict[str, Any]:
    """Apply ML-based conflict resolution"""
    if SIMULATION_MODE:
        # Simulate ML model prediction
        import random
        
        agents = list(conflict_set.positions.keys())
        confidence = random.uniform(0.7, 0.95)
        winner = random.choice(agents)
        
        resolution = {
            "method": "ml_based",
            "model": "conflict_resolver_v1.2",
            "winner": winner,
            "winning_position": conflict_set.positions[winner],
            "confidence": confidence,
            "rationale": f"ML model predicts agent {winner} has optimal solution (confidence: {confidence:.2f})"
        }
        
        return resolution
    
    # In production: actual ML model inference
    return {"method": "ml_based", "error": "ML model not available"}

def calculate_resolution_confidence(resolution: Dict[str, Any], conflict_type: str) -> float:
    """Calculate confidence score for resolution"""
    base_confidence = 0.8
    
    # Adjust based on resolution method
    if resolution["method"] == "rule_based":
        # Rule-based resolutions are generally reliable
        base_confidence = 0.85
    elif resolution["method"] == "ml_based":
        # Use ML model confidence if available
        base_confidence = resolution.get("confidence", 0.75)
    elif resolution["method"] == "human":
        # Human decisions are highly confident
        base_confidence = 0.95
    
    # Adjust based on conflict complexity
    if conflict_type in ["security_conflicts", "policy_conflicts"]:
        base_confidence += 0.05  # These have clearer rules
    elif conflict_type == "performance_conflicts":
        base_confidence -= 0.05  # More subjective
    
    return min(base_confidence, 1.0)

@app.post("/v1/arbiter/decide")
async def arbitrate_conflict(request: ArbitrationRequest):
    """Arbitrate conflict and return decision"""
    with ARBITRATION_DURATION.time():
        conflict_set = request.conflict_set
        conflict_id = conflict_set.conflict_id
        
        # Store conflict
        conflicts[conflict_id] = conflict_set
        
        # Classify conflict
        conflict_type = classify_conflict(conflict_set)
        
        # Choose resolution method
        resolution_method = request.resolution_method
        if resolution_method == "auto":
            # Auto-select based on conflict type and priority
            if request.priority in ["high", "urgent"]:
                resolution_method = "rules"
            elif conflict_type in ["security_conflicts", "policy_conflicts"]:
                resolution_method = "rules"
            else:
                resolution_method = "ml"
        
        # Apply resolution
        if resolution_method == "rules":
            resolution = apply_rule_based_resolution(conflict_set, conflict_type)
        elif resolution_method == "ml":
            resolution = apply_ml_resolution(conflict_set)
        else:
            # Default to rules
            resolution = apply_rule_based_resolution(conflict_set, conflict_type)
        
        # Calculate confidence
        confidence = calculate_resolution_confidence(resolution, conflict_type)
        
        # Create decision record
        decision_id = f"dec-{conflict_id}-{datetime.utcnow().strftime('%H%M%S')}"
        
        decision = DecisionRecord(
            decision_id=decision_id,
            conflict_id=conflict_id,
            resolution=resolution,
            confidence=confidence,
            method=resolution.get("method", resolution_method),
            rationale=resolution.get("rationale", "Automated arbitration"),
            timestamp=datetime.utcnow().isoformat(),
            metadata={
                "conflict_type": conflict_type,
                "agents_count": len(conflict_set.agents),
                "priority": request.priority
            }
        )
        
        decisions[decision_id] = decision
        
        CONFLICTS_RESOLVED.labels(resolution_method=decision.method).inc()
        RESOLUTION_CONFIDENCE.observe(confidence)
        
        logger.info(f"Resolved conflict {conflict_id} using {decision.method} (confidence: {confidence:.2f})")
        
        return {
            "decision_id": decision_id,
            "conflict_id": conflict_id,
            "resolution": resolution,
            "confidence": confidence,
            "method": decision.method,
            "timestamp": decision.timestamp
        }

@app.get("/v1/conflicts/{conflict_id}")
async def get_conflict(conflict_id: str):
    """Get conflict details"""
    if conflict_id not in conflicts:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    conflict = conflicts[conflict_id]
    
    # Find associated decisions
    conflict_decisions = [d for d in decisions.values() if d.conflict_id == conflict_id]
    
    return {
        "conflict": conflict.dict(),
        "decisions": [d.dict() for d in conflict_decisions]
    }

@app.get("/v1/decisions/{decision_id}")
async def get_decision(decision_id: str):
    """Get decision details"""
    if decision_id not in decisions:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    return decisions[decision_id].dict()

@app.get("/v1/rules")
async def get_arbitration_rules():
    """Get available arbitration rules"""
    return {
        "rules": load_arbitration_rules(),
        "conflict_types": [
            "resource_conflicts",
            "policy_conflicts", 
            "performance_conflicts",
            "security_conflicts",
            "cost_conflicts"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "arbiter",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "conflicts_processed": len(conflicts),
        "decisions_made": len(decisions)
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return JSONResponse(
        content=generate_latest().decode('utf-8'),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)