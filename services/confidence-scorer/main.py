#!/usr/bin/env python3
"""
Phase I.4.4 - Confidence Scorer
Produces confidence, risk, cost tradeoff metrics and explanation text
"""

import os
import json
import math
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
SCORES_TOTAL = Counter('confidence_scores_total', 'Total confidence scores generated')
SCORING_DURATION = Histogram('scoring_duration_seconds', 'Scoring processing time')

app = FastAPI(title="Confidence Scorer", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
NEURAL_FABRIC_URL = os.getenv('NEURAL_FABRIC_URL', 'http://localhost:8080')

class ScoreRequest(BaseModel):
    proposal_id: str
    manifest: Optional[Dict[str, Any]] = {}
    historical_context: Optional[Dict[str, Any]] = {}

class ConfidenceScore(BaseModel):
    confidence: float  # 0.0 to 1.0
    risk: float       # 0.0 to 1.0
    cost_estimate: Optional[float] = None
    explanation: str
    factors: Dict[str, Any]
    model_version: str = "1.0.0"

def calculate_action_confidence(action: str, target: str) -> float:
    """Calculate confidence based on action type and target"""
    action_confidence_map = {
        "scale_up": 0.85,
        "scale_down": 0.75,
        "security_patch": 0.90,
        "update_config": 0.80,
        "restart_service": 0.70,
        "deploy_new": 0.60,
        "delete": 0.40,
        "emergency_action": 0.50
    }
    
    base_confidence = action_confidence_map.get(action, 0.65)
    
    # Adjust based on target complexity
    target_complexity = {
        "compute_instances": 0.9,
        "database": 0.7,
        "network_config": 0.6,
        "security_groups": 0.8,
        "load_balancer": 0.85
    }
    
    complexity_factor = target_complexity.get(target, 0.75)
    return min(base_confidence * complexity_factor, 1.0)

def calculate_risk_score(manifest: Dict[str, Any]) -> float:
    """Calculate risk score based on manifest content"""
    base_risk = 0.3
    
    # Risk factors
    impact_level = manifest.get('impact_level', 'medium')
    impact_risk = {
        'low': 0.1,
        'medium': 0.3,
        'high': 0.7,
        'critical': 0.9
    }
    
    action = manifest.get('action', '')
    action_risk = {
        'scale_up': 0.2,
        'scale_down': 0.4,
        'security_patch': 0.3,
        'delete': 0.8,
        'emergency_action': 0.9,
        'restart_service': 0.5
    }
    
    # Calculate composite risk
    risk = impact_risk.get(impact_level, 0.3)
    risk += action_risk.get(action, 0.3)
    
    # Additional risk factors
    if not manifest.get('rollback_plan', False):
        risk += 0.2
    
    if not manifest.get('approval_required', False) and impact_level == 'high':
        risk += 0.3
    
    return min(risk, 1.0)

def estimate_cost_impact(manifest: Dict[str, Any]) -> float:
    """Estimate cost impact of the proposed action"""
    action = manifest.get('action', '')
    parameters = manifest.get('parameters', {})
    
    # Base cost estimates (in USD)
    action_costs = {
        'scale_up': 100.0,
        'scale_down': -50.0,
        'security_patch': 25.0,
        'deploy_new': 200.0,
        'restart_service': 10.0,
        'update_config': 5.0
    }
    
    base_cost = action_costs.get(action, 50.0)
    
    # Adjust based on parameters
    if 'target_count' in parameters:
        count_multiplier = parameters['target_count'] / 2.0  # Assume baseline of 2
        base_cost *= count_multiplier
    
    if 'instance_type' in parameters:
        instance_type = parameters['instance_type']
        type_multipliers = {
            't3.micro': 0.5,
            't3.small': 0.7,
            't3.medium': 1.0,
            'c5.large': 1.5,
            'c5.xlarge': 2.0,
            'm5.large': 1.3
        }
        base_cost *= type_multipliers.get(instance_type, 1.0)
    
    return round(base_cost, 2)

def get_historical_performance(action: str, target: str) -> Dict[str, float]:
    """Get simulated historical performance metrics"""
    # Simulate historical success rates
    historical_data = {
        ("scale_up", "compute_instances"): {"success_rate": 0.92, "avg_duration": 300},
        ("scale_down", "compute_instances"): {"success_rate": 0.88, "avg_duration": 180},
        ("security_patch", "system"): {"success_rate": 0.95, "avg_duration": 600},
        ("restart_service", "application"): {"success_rate": 0.85, "avg_duration": 120}
    }
    
    key = (action, target)
    return historical_data.get(key, {"success_rate": 0.75, "avg_duration": 240})

def generate_explanation(confidence: float, risk: float, factors: Dict[str, Any]) -> str:
    """Generate human-readable explanation"""
    explanation_parts = []
    
    # Confidence explanation
    if confidence >= 0.8:
        explanation_parts.append("High confidence based on proven action patterns")
    elif confidence >= 0.6:
        explanation_parts.append("Moderate confidence with some uncertainty factors")
    else:
        explanation_parts.append("Lower confidence due to complexity or limited precedent")
    
    # Risk explanation
    if risk >= 0.7:
        explanation_parts.append("High risk operation requiring careful monitoring")
    elif risk >= 0.4:
        explanation_parts.append("Moderate risk with standard safety measures")
    else:
        explanation_parts.append("Low risk operation with minimal impact")
    
    # Factor-specific explanations
    if factors.get('historical_success_rate', 0) < 0.8:
        explanation_parts.append("Historical success rate indicates potential challenges")
    
    if not factors.get('rollback_available', True):
        explanation_parts.append("Limited rollback capability increases risk")
    
    if factors.get('impact_level') == 'high':
        explanation_parts.append("High impact level requires additional approval")
    
    return ". ".join(explanation_parts) + "."

@app.post("/score")
async def score_proposal(request: ScoreRequest):
    """Generate confidence and risk scores for proposal"""
    SCORES_TOTAL.inc()
    
    manifest = request.manifest
    action = manifest.get('action', 'unknown')
    target = manifest.get('target', 'system')
    
    # Calculate confidence
    confidence = calculate_action_confidence(action, target)
    
    # Calculate risk
    risk = calculate_risk_score(manifest)
    
    # Estimate cost
    cost_estimate = estimate_cost_impact(manifest)
    
    # Get historical performance
    historical = get_historical_performance(action, target)
    
    # Adjust confidence based on historical performance
    confidence *= historical['success_rate']
    
    # Compile factors
    factors = {
        'action_type': action,
        'target_system': target,
        'impact_level': manifest.get('impact_level', 'medium'),
        'historical_success_rate': historical['success_rate'],
        'estimated_duration': historical['avg_duration'],
        'rollback_available': manifest.get('rollback_plan', False),
        'approval_required': manifest.get('approval_required', False),
        'safety_checks': len(manifest.get('safety_checks', [])),
        'parameters_complexity': len(manifest.get('parameters', {}))
    }
    
    # Generate explanation
    explanation = generate_explanation(confidence, risk, factors)
    
    # Create score object
    score = ConfidenceScore(
        confidence=round(confidence, 3),
        risk=round(risk, 3),
        cost_estimate=cost_estimate,
        explanation=explanation,
        factors=factors
    )
    
    logger.info(f"Generated score for proposal {request.proposal_id}: confidence={score.confidence}, risk={score.risk}")
    
    return {
        "proposal_id": request.proposal_id,
        "score": score.dict(),
        "timestamp": datetime.utcnow().isoformat(),
        "model_version": "1.0.0"
    }

@app.post("/batch_score")
async def batch_score_proposals(proposals: List[ScoreRequest]):
    """Score multiple proposals in batch"""
    results = []
    
    for proposal in proposals:
        try:
            score_result = await score_proposal(proposal)
            results.append(score_result)
        except Exception as e:
            results.append({
                "proposal_id": proposal.proposal_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    return {
        "batch_results": results,
        "total_processed": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/models")
async def list_scoring_models():
    """List available scoring models and their capabilities"""
    return {
        "models": [
            {
                "name": "confidence_v1",
                "version": "1.0.0",
                "description": "Action-based confidence scoring with historical data",
                "capabilities": ["confidence", "risk", "cost_estimation"]
            },
            {
                "name": "risk_analyzer_v1", 
                "version": "1.0.0",
                "description": "Multi-factor risk assessment model",
                "capabilities": ["risk", "impact_analysis", "safety_scoring"]
            }
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint (P4)"""
    return {
        "status": "healthy",
        "service": "confidence-scorer",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "models_loaded": 2
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
    uvicorn.run(app, host="0.0.0.0", port=9204)