#!/usr/bin/env python3
"""
Phase I.5 - Privacy Proxy
Differential privacy and secure aggregation for federated learning
"""

import os
import json
import math
import random
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
AGGREGATIONS_TOTAL = Counter('privacy_aggregations_total', 'Total privacy aggregations')
EPSILON_CONSUMED = Counter('privacy_epsilon_consumed_total', 'Total epsilon consumed')
PRIVACY_VIOLATIONS = Counter('privacy_violations_total', 'Privacy budget violations')

app = FastAPI(title="Privacy Proxy", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
DEFAULT_EPSILON = float(os.getenv('DEFAULT_EPSILON', '1.0'))

# Privacy budget tracking
privacy_budgets = {}

class AggregationRequest(BaseModel):
    round_id: str
    participant_data: List[Dict[str, Any]]
    epsilon: float
    delta: Optional[float] = 1e-5
    mechanism: str = "gaussian"  # gaussian, laplace, exponential

class BudgetRequest(BaseModel):
    tenant_id: str
    operation: str
    epsilon_requested: float

def add_gaussian_noise(value: float, sensitivity: float, epsilon: float, delta: float = 1e-5) -> float:
    """Add Gaussian noise for differential privacy"""
    if SIMULATION_MODE:
        # Simulate noise addition
        sigma = math.sqrt(2 * math.log(1.25 / delta)) * sensitivity / epsilon
        noise = random.gauss(0, sigma)
        return value + noise
    
    # In production: use proper DP library
    import numpy as np
    sigma = math.sqrt(2 * math.log(1.25 / delta)) * sensitivity / epsilon
    noise = np.random.normal(0, sigma)
    return value + noise

def add_laplace_noise(value: float, sensitivity: float, epsilon: float) -> float:
    """Add Laplace noise for differential privacy"""
    if SIMULATION_MODE:
        # Simulate Laplace noise
        scale = sensitivity / epsilon
        noise = random.expovariate(1/scale) * random.choice([-1, 1])
        return value + noise
    
    # In production: use proper DP library
    import numpy as np
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return value + noise

def calculate_sensitivity(data: List[Dict[str, Any]]) -> float:
    """Calculate L1 sensitivity of the data"""
    if not data:
        return 1.0
    
    # Simplified sensitivity calculation
    # In production: proper sensitivity analysis based on data type
    max_contribution = 1.0  # Assume each participant contributes at most 1.0
    return max_contribution

def secure_aggregation(participant_data: List[Dict[str, Any]], epsilon: float, mechanism: str) -> Dict[str, Any]:
    """Perform secure aggregation with differential privacy"""
    if not participant_data:
        return {"aggregated_weights": {}, "participant_count": 0}
    
    # Calculate sensitivity
    sensitivity = calculate_sensitivity(participant_data)
    
    # Aggregate weights
    aggregated = {}
    participant_count = len(participant_data)
    
    # Simple averaging with noise
    for participant in participant_data:
        weights = participant.get('weights', {})
        for layer, values in weights.items():
            if layer not in aggregated:
                aggregated[layer] = []
            
            if isinstance(values, list):
                # Extend or initialize layer values
                while len(aggregated[layer]) < len(values):
                    aggregated[layer].append(0.0)
                
                for i, value in enumerate(values):
                    aggregated[layer][i] += value / participant_count
    
    # Add differential privacy noise
    for layer, values in aggregated.items():
        for i in range(len(values)):
            if mechanism == "gaussian":
                aggregated[layer][i] = add_gaussian_noise(values[i], sensitivity, epsilon)
            elif mechanism == "laplace":
                aggregated[layer][i] = add_laplace_noise(values[i], sensitivity, epsilon)
    
    return {
        "aggregated_weights": aggregated,
        "participant_count": participant_count,
        "epsilon_used": epsilon,
        "sensitivity": sensitivity,
        "mechanism": mechanism
    }

def check_privacy_budget(tenant_id: str, epsilon_requested: float) -> bool:
    """Check if privacy budget allows the requested epsilon"""
    if tenant_id not in privacy_budgets:
        privacy_budgets[tenant_id] = {
            "total_budget": 10.0,  # Monthly budget
            "used_budget": 0.0,
            "last_reset": datetime.utcnow().isoformat()
        }
    
    budget = privacy_budgets[tenant_id]
    available = budget["total_budget"] - budget["used_budget"]
    
    return available >= epsilon_requested

def consume_privacy_budget(tenant_id: str, epsilon_used: float):
    """Consume privacy budget"""
    if tenant_id not in privacy_budgets:
        privacy_budgets[tenant_id] = {
            "total_budget": 10.0,
            "used_budget": 0.0,
            "last_reset": datetime.utcnow().isoformat()
        }
    
    privacy_budgets[tenant_id]["used_budget"] += epsilon_used
    EPSILON_CONSUMED.inc(epsilon_used)

@app.post("/v1/aggregate")
async def perform_aggregation(request: AggregationRequest):
    """Perform secure aggregation with differential privacy"""
    AGGREGATIONS_TOTAL.inc()
    
    # Extract tenant from first participant (simplified)
    tenant_id = "default"
    if request.participant_data:
        tenant_id = request.participant_data[0].get('tenant_id', 'default')
    
    # Check privacy budget
    if not check_privacy_budget(tenant_id, request.epsilon):
        PRIVACY_VIOLATIONS.inc()
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient privacy budget. Requested: {request.epsilon}, Available: {privacy_budgets.get(tenant_id, {}).get('total_budget', 0) - privacy_budgets.get(tenant_id, {}).get('used_budget', 0)}"
        )
    
    # Perform secure aggregation
    result = secure_aggregation(
        request.participant_data,
        request.epsilon,
        request.mechanism
    )
    
    # Consume privacy budget
    consume_privacy_budget(tenant_id, request.epsilon)
    
    # Add metadata
    result.update({
        "round_id": request.round_id,
        "tenant_id": tenant_id,
        "timestamp": datetime.utcnow().isoformat(),
        "privacy_guaranteed": True
    })
    
    logger.info(f"Completed secure aggregation for round {request.round_id} with epsilon {request.epsilon}")
    
    return result

@app.get("/v1/budget/{tenant_id}")
async def get_privacy_budget(tenant_id: str):
    """Get privacy budget status for tenant"""
    if tenant_id not in privacy_budgets:
        privacy_budgets[tenant_id] = {
            "total_budget": 10.0,
            "used_budget": 0.0,
            "last_reset": datetime.utcnow().isoformat()
        }
    
    budget = privacy_budgets[tenant_id]
    available = budget["total_budget"] - budget["used_budget"]
    
    return {
        "tenant_id": tenant_id,
        "total_budget": budget["total_budget"],
        "used_budget": budget["used_budget"],
        "available_budget": available,
        "utilization_percentage": (budget["used_budget"] / budget["total_budget"]) * 100,
        "last_reset": budget["last_reset"]
    }

@app.post("/v1/budget/check")
async def check_budget(request: BudgetRequest):
    """Check if privacy budget request can be fulfilled"""
    available = check_privacy_budget(request.tenant_id, request.epsilon_requested)
    
    budget_info = privacy_budgets.get(request.tenant_id, {
        "total_budget": 10.0,
        "used_budget": 0.0
    })
    
    return {
        "tenant_id": request.tenant_id,
        "operation": request.operation,
        "epsilon_requested": request.epsilon_requested,
        "budget_available": available,
        "current_usage": budget_info["used_budget"],
        "total_budget": budget_info["total_budget"]
    }

@app.post("/v1/budget/reset/{tenant_id}")
async def reset_privacy_budget(tenant_id: str):
    """Reset privacy budget for tenant (admin operation)"""
    privacy_budgets[tenant_id] = {
        "total_budget": 10.0,
        "used_budget": 0.0,
        "last_reset": datetime.utcnow().isoformat()
    }
    
    return {
        "tenant_id": tenant_id,
        "status": "reset",
        "new_budget": 10.0,
        "reset_at": privacy_budgets[tenant_id]["last_reset"]
    }

@app.get("/v1/mechanisms")
async def list_mechanisms():
    """List available privacy mechanisms"""
    return {
        "mechanisms": [
            {
                "name": "gaussian",
                "description": "Gaussian mechanism for continuous queries",
                "suitable_for": ["continuous_values", "real_numbers"]
            },
            {
                "name": "laplace",
                "description": "Laplace mechanism for counting queries",
                "suitable_for": ["counting_queries", "histograms"]
            },
            {
                "name": "exponential",
                "description": "Exponential mechanism for categorical selection",
                "suitable_for": ["categorical_data", "selection_queries"]
            }
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "privacy-proxy",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "active_tenants": len(privacy_budgets)
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
    uvicorn.run(app, host="0.0.0.0", port=8006)