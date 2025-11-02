#!/usr/bin/env python3
"""
Phase I.5 - Policy Engine
Centralized policy evaluation and enforcement
"""

import os
import json
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
POLICY_EVALUATIONS = Counter('policy_evaluations_total', 'Total policy evaluations', ['policy', 'decision'])
POLICY_VIOLATIONS = Counter('policy_violations_total', 'Total policy violations', ['policy'])
EVALUATION_LATENCY = Histogram('policy_evaluation_latency_seconds', 'Policy evaluation latency')

app = FastAPI(title="Policy Engine", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
POLICY_CONFIG_PATH = os.getenv('POLICY_CONFIG_PATH', '/infra/vault/policies/collective-intelligence.hcl')

# Policy cache
policy_matrix = {}
policy_rules = {}

class PolicyEvaluationRequest(BaseModel):
    context: str
    resource: Dict[str, Any]
    actor: Dict[str, Any]
    action: str
    metadata: Optional[Dict[str, Any]] = {}

class PolicyDecision(BaseModel):
    decision: str  # allow, deny, transform
    policy_matched: str
    confidence: float
    rationale: str
    transformations: Optional[List[Dict[str, Any]]] = []
    conditions: Optional[List[str]] = []

def load_policy_matrix():
    """Load policy matrix from configuration"""
    global policy_matrix, policy_rules
    
    try:
        if SIMULATION_MODE:
            # Load from global infra directory
            policy_path = "infra/vault/policies/collective-intelligence.hcl"
            if os.path.exists(policy_path):
                with open(policy_path, 'r') as f:
                    config = yaml.safe_load(f)
                    policy_matrix = config.get('policy_matrix', {})
                    policy_rules = config.get('enforcement_levels', [])
            else:
                # Default policy matrix
                policy_matrix = {
                    "data_ingest": {
                        "enforcement_point": "signal-gateway",
                        "enforcement_mode": "Reject/Mask",
                        "rules": [
                            {"name": "pii_protection", "condition": "classification == 'confidential'", "action": "require_consent_token"},
                            {"name": "tenant_isolation", "condition": "tenant_id != null", "action": "enforce_tenant_scope"}
                        ]
                    },
                    "model_updates": {
                        "enforcement_point": "fl-orchestrator",
                        "enforcement_mode": "Block pre-commit",
                        "rules": [
                            {"name": "fairness_validation", "condition": "fairness_score >= 0.8", "action": "allow_aggregation"},
                            {"name": "privacy_budget", "condition": "epsilon_used <= epsilon_limit", "action": "allow_aggregation"}
                        ]
                    }
                }
        
        logger.info(f"Loaded {len(policy_matrix)} policy areas")
        
    except Exception as e:
        logger.error(f"Error loading policy matrix: {e}")
        policy_matrix = {}

def evaluate_condition(condition: str, context: Dict[str, Any]) -> bool:
    """Evaluate policy condition against context"""
    try:
        # Simple condition evaluation (in production: use proper policy language)
        if "==" in condition:
            left, right = condition.split("==")
            left = left.strip()
            right = right.strip().strip("'\"")
            
            # Navigate nested context
            value = context
            for key in left.split("."):
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return False
            
            return str(value) == right
        
        elif ">=" in condition:
            left, right = condition.split(">=")
            left = left.strip()
            right = float(right.strip())
            
            value = context
            for key in left.split("."):
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return False
            
            return float(value) >= right
        
        elif "!=" in condition:
            left, right = condition.split("!=")
            left = left.strip()
            right = right.strip()
            
            value = context
            for key in left.split("."):
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return True  # If key doesn't exist, != null is true
            
            return value != (None if right == "null" else right.strip("'\""))
        
        return True  # Default allow for unknown conditions
        
    except Exception as e:
        logger.warning(f"Error evaluating condition '{condition}': {e}")
        return False

def find_matching_policy(context: str, resource: Dict[str, Any], action: str) -> Optional[Dict[str, Any]]:
    """Find matching policy for the given context"""
    # Map contexts to policy areas
    context_mapping = {
        "signal_ingest": "data_ingest",
        "data_ingest": "data_ingest",
        "model_update": "model_updates",
        "fl_round": "model_updates",
        "access_control": "access_control",
        "privacy": "privacy_protection",
        "audit": "audit_compliance"
    }
    
    policy_area = context_mapping.get(context, context)
    
    if policy_area in policy_matrix:
        return policy_matrix[policy_area]
    
    return None

def evaluate_policy_rules(policy: Dict[str, Any], context_data: Dict[str, Any]) -> PolicyDecision:
    """Evaluate policy rules against context data"""
    rules = policy.get("rules", [])
    enforcement_mode = policy.get("enforcement_mode", "Block")
    
    for rule in rules:
        rule_name = rule.get("name", "unknown")
        condition = rule.get("condition", "true")
        action = rule.get("action", "deny")
        
        if evaluate_condition(condition, context_data):
            # Rule matched
            if action in ["allow", "allow_aggregation", "grant_access", "allow_operation"]:
                return PolicyDecision(
                    decision="allow",
                    policy_matched=rule_name,
                    confidence=0.95,
                    rationale=f"Rule '{rule_name}' allows action based on condition: {condition}"
                )
            elif action in ["require_consent_token", "require_mfa", "apply_dp_noise"]:
                return PolicyDecision(
                    decision="transform",
                    policy_matched=rule_name,
                    confidence=0.90,
                    rationale=f"Rule '{rule_name}' requires transformation: {action}",
                    transformations=[{"type": action, "condition": condition}]
                )
            else:
                return PolicyDecision(
                    decision="deny",
                    policy_matched=rule_name,
                    confidence=0.95,
                    rationale=f"Rule '{rule_name}' denies action based on condition: {condition}"
                )
    
    # No rules matched - default based on enforcement mode
    if enforcement_mode in ["Block", "Block pre-commit"]:
        return PolicyDecision(
            decision="deny",
            policy_matched="default_deny",
            confidence=0.80,
            rationale="No matching rules found, default deny policy applied"
        )
    else:
        return PolicyDecision(
            decision="allow",
            policy_matched="default_allow",
            confidence=0.70,
            rationale="No matching rules found, default allow policy applied"
        )

@app.post("/v1/evaluate")
async def evaluate_policy(request: PolicyEvaluationRequest):
    """Evaluate policy for given context and resource"""
    with EVALUATION_LATENCY.time():
        # Find matching policy
        policy = find_matching_policy(request.context, request.resource, request.action)
        
        if not policy:
            # No policy found - default allow
            decision = PolicyDecision(
                decision="allow",
                policy_matched="no_policy",
                confidence=0.50,
                rationale=f"No policy found for context '{request.context}', defaulting to allow"
            )
        else:
            # Combine all context for evaluation
            context_data = {
                **request.resource,
                **request.actor,
                **request.metadata,
                "action": request.action,
                "context": request.context
            }
            
            # Evaluate policy rules
            decision = evaluate_policy_rules(policy, context_data)
        
        # Record metrics
        POLICY_EVALUATIONS.labels(
            policy=decision.policy_matched,
            decision=decision.decision
        ).inc()
        
        if decision.decision == "deny":
            POLICY_VIOLATIONS.labels(policy=decision.policy_matched).inc()
        
        logger.info(f"Policy evaluation: {request.context} -> {decision.decision} ({decision.policy_matched})")
        
        return {
            "request_id": f"eval-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "decision": decision.dict(),
            "evaluated_at": datetime.utcnow().isoformat()
        }

@app.post("/v1/batch_evaluate")
async def batch_evaluate_policies(requests: List[PolicyEvaluationRequest]):
    """Batch evaluate multiple policy requests"""
    results = []
    
    for request in requests:
        try:
            result = await evaluate_policy(request)
            results.append({
                "context": request.context,
                "action": request.action,
                "result": result
            })
        except Exception as e:
            results.append({
                "context": request.context,
                "action": request.action,
                "error": str(e)
            })
    
    return {
        "batch_size": len(requests),
        "results": results,
        "evaluated_at": datetime.utcnow().isoformat()
    }

@app.get("/v1/policies")
async def list_policies():
    """List all available policies"""
    return {
        "policy_areas": list(policy_matrix.keys()),
        "policies": policy_matrix,
        "loaded_at": datetime.utcnow().isoformat()
    }

@app.get("/v1/policies/{policy_area}")
async def get_policy(policy_area: str):
    """Get specific policy details"""
    if policy_area not in policy_matrix:
        raise HTTPException(status_code=404, detail="Policy area not found")
    
    return {
        "policy_area": policy_area,
        "policy": policy_matrix[policy_area]
    }

@app.post("/v1/policies/reload")
async def reload_policies():
    """Reload policies from configuration"""
    load_policy_matrix()
    
    return {
        "status": "reloaded",
        "policy_areas": len(policy_matrix),
        "reloaded_at": datetime.utcnow().isoformat()
    }

@app.get("/v1/test/{context}")
async def test_policy(
    context: str,
    classification: Optional[str] = None,
    tenant_id: Optional[str] = None,
    fairness_score: Optional[float] = None,
    epsilon_used: Optional[float] = None
):
    """Test policy evaluation with sample data"""
    test_resource = {}
    if classification:
        test_resource["classification"] = classification
    if tenant_id:
        test_resource["tenant_id"] = tenant_id
    if fairness_score is not None:
        test_resource["fairness_score"] = fairness_score
    if epsilon_used is not None:
        test_resource["epsilon_used"] = epsilon_used
        test_resource["epsilon_limit"] = 1.0  # Default limit
    
    test_request = PolicyEvaluationRequest(
        context=context,
        resource=test_resource,
        actor={"user_id": "test-user"},
        action="test_action"
    )
    
    return await evaluate_policy(test_request)

# Load policies on startup
load_policy_matrix()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "policy-engine",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "policies_loaded": len(policy_matrix)
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
    uvicorn.run(app, host="0.0.0.0", port=8008)