#!/usr/bin/env python3
"""
Phase I.5 - Federated Learning Orchestrator
Coordinates federated learning rounds, model validation, and secure aggregation
"""

import os
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
FL_ROUNDS_STARTED = Counter('fl_rounds_started_total', 'Total FL rounds started')
FL_ROUNDS_COMPLETED = Counter('fl_rounds_completed_total', 'Total FL rounds completed', ['status'])
MODEL_VALIDATIONS = Counter('model_validations_total', 'Total model validations', ['result'])
FL_ROUND_DURATION = Histogram('fl_round_duration_seconds', 'FL round duration')

app = FastAPI(title="FL Orchestrator", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
EPSILON_BUDGET_DEFAULT = float(os.getenv('EPSILON_BUDGET_DEFAULT', '1.0'))

# In-memory storage for simulation
fl_rounds = {}
model_deltas = {}
validation_results = {}

class ModelDeltaV1(BaseModel):
    delta_id: str
    round_id: str
    participant_id: str
    delta_data: Dict[str, Any]  # Tensor metadata, weights, etc.
    metadata: Dict[str, Any]
    signature: str
    timestamp: str

class FLRoundRequest(BaseModel):
    round_id: str
    model_base: str
    participants: List[str]
    epsilon_budget: Optional[float] = EPSILON_BUDGET_DEFAULT
    timeout_minutes: Optional[int] = 60
    validation_config: Optional[Dict[str, Any]] = {}

class ValidationResult(BaseModel):
    validation_id: str
    delta_id: str
    passed: bool
    score: float
    checks: Dict[str, Any]
    timestamp: str

def generate_round_id() -> str:
    """Generate unique FL round ID"""
    return f"fl-round-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

def validate_model_delta(delta: ModelDeltaV1, validation_config: Dict[str, Any]) -> ValidationResult:
    """Validate model delta against fairness and quality metrics"""
    checks = {}
    score = 0.0
    
    # Check 1: Signature validation
    delta_str = json.dumps({
        "delta_id": delta.delta_id,
        "round_id": delta.round_id,
        "participant_id": delta.participant_id,
        "delta_data": delta.delta_data
    }, sort_keys=True)
    expected_sig = hashlib.sha256(delta_str.encode()).hexdigest()[:16]
    
    checks["signature_valid"] = delta.signature == expected_sig
    if checks["signature_valid"]:
        score += 0.3
    
    # Check 2: Delta size validation
    delta_size = len(json.dumps(delta.delta_data))
    max_size = validation_config.get("max_delta_size", 1024 * 1024)  # 1MB default
    checks["size_valid"] = delta_size <= max_size
    if checks["size_valid"]:
        score += 0.2
    
    # Check 3: Fairness metrics (simulated)
    fairness_score = 0.85  # Simulate fairness calculation
    fairness_threshold = validation_config.get("fairness_threshold", 0.8)
    checks["fairness_valid"] = fairness_score >= fairness_threshold
    checks["fairness_score"] = fairness_score
    if checks["fairness_valid"]:
        score += 0.3
    
    # Check 4: Privacy budget validation
    epsilon_used = delta.metadata.get("epsilon_used", 0.1)
    epsilon_limit = validation_config.get("epsilon_limit", 1.0)
    checks["privacy_valid"] = epsilon_used <= epsilon_limit
    checks["epsilon_used"] = epsilon_used
    if checks["privacy_valid"]:
        score += 0.2
    
    passed = score >= 0.8  # Require 80% score to pass
    
    validation_id = f"val-{delta.delta_id}-{datetime.utcnow().strftime('%H%M%S')}"
    
    return ValidationResult(
        validation_id=validation_id,
        delta_id=delta.delta_id,
        passed=passed,
        score=score,
        checks=checks,
        timestamp=datetime.utcnow().isoformat()
    )

async def aggregate_deltas(deltas: List[ModelDeltaV1]) -> Dict[str, Any]:
    """Perform secure aggregation of model deltas"""
    if SIMULATION_MODE:
        # Simulate secure aggregation
        logger.info(f"Simulating secure aggregation of {len(deltas)} deltas")
        
        # Simulate aggregated weights
        aggregated_model = {
            "model_id": f"aggregated-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "participant_count": len(deltas),
            "aggregation_method": "federated_averaging",
            "weights": {
                "layer_1": [0.1, 0.2, 0.3],  # Simulated weights
                "layer_2": [0.4, 0.5, 0.6],
                "output": [0.7, 0.8, 0.9]
            },
            "metadata": {
                "aggregated_at": datetime.utcnow().isoformat(),
                "total_samples": sum(d.metadata.get("sample_count", 100) for d in deltas),
                "privacy_budget_used": sum(d.metadata.get("epsilon_used", 0.1) for d in deltas)
            }
        }
        
        await asyncio.sleep(2)  # Simulate computation time
        return aggregated_model
    
    # In production: actual secure aggregation
    return {}

async def store_model_artifact(model: Dict[str, Any], round_id: str) -> str:
    """Store aggregated model in model-store"""
    if SIMULATION_MODE:
        # Simulate model storage
        model_hash = hashlib.sha256(json.dumps(model, sort_keys=True).encode()).hexdigest()
        artifact_id = f"model-{round_id}-{model_hash[:16]}"
        
        logger.info(f"Simulating model storage: {artifact_id}")
        await asyncio.sleep(1)  # Simulate storage time
        
        return artifact_id
    
    # In production: actual model-store API call
    return "production-artifact-id"

async def conduct_fl_round(round_id: str, fl_request: FLRoundRequest):
    """Conduct complete FL round"""
    try:
        fl_round = fl_rounds[round_id]
        fl_round["status"] = "collecting_deltas"
        
        # Wait for model deltas from participants
        timeout_at = datetime.utcnow() + timedelta(minutes=fl_request.timeout_minutes)
        collected_deltas = []
        
        while datetime.utcnow() < timeout_at and len(collected_deltas) < len(fl_request.participants):
            # Check for new deltas
            for delta_id, delta in model_deltas.items():
                if (delta.round_id == round_id and 
                    delta.participant_id in fl_request.participants and
                    delta not in collected_deltas):
                    
                    # Validate delta
                    validation = validate_model_delta(delta, fl_request.validation_config)
                    validation_results[validation.validation_id] = validation
                    
                    MODEL_VALIDATIONS.labels(
                        result='passed' if validation.passed else 'failed'
                    ).inc()
                    
                    if validation.passed:
                        collected_deltas.append(delta)
                        logger.info(f"Accepted delta {delta.delta_id} for round {round_id}")
                    else:
                        logger.warning(f"Rejected delta {delta.delta_id}: validation failed")
            
            await asyncio.sleep(5)  # Check every 5 seconds
        
        # Check if we have enough deltas
        min_participants = max(2, len(fl_request.participants) // 2)  # At least 50%
        if len(collected_deltas) < min_participants:
            fl_round["status"] = "failed"
            fl_round["error"] = f"Insufficient participants: {len(collected_deltas)}/{len(fl_request.participants)}"
            FL_ROUNDS_COMPLETED.labels(status='failed').inc()
            return
        
        # Perform secure aggregation
        fl_round["status"] = "aggregating"
        aggregated_model = await aggregate_deltas(collected_deltas)
        
        # Store model artifact
        fl_round["status"] = "storing"
        artifact_id = await store_model_artifact(aggregated_model, round_id)
        
        # Complete round
        fl_round["status"] = "completed"
        fl_round["artifact_id"] = artifact_id
        fl_round["participants_count"] = len(collected_deltas)
        fl_round["completed_at"] = datetime.utcnow().isoformat()
        
        FL_ROUNDS_COMPLETED.labels(status='completed').inc()
        logger.info(f"FL round {round_id} completed successfully")
        
    except Exception as e:
        fl_round["status"] = "error"
        fl_round["error"] = str(e)
        FL_ROUNDS_COMPLETED.labels(status='error').inc()
        logger.error(f"FL round {round_id} failed: {e}")

@app.post("/v1/fl/round")
async def start_fl_round(
    request: FLRoundRequest,
    background_tasks: BackgroundTasks
):
    """Start federated learning round"""
    FL_ROUNDS_STARTED.inc()
    
    round_id = request.round_id or generate_round_id()
    
    # Create FL round record
    fl_round = {
        "round_id": round_id,
        "model_base": request.model_base,
        "participants": request.participants,
        "epsilon_budget": request.epsilon_budget,
        "timeout_minutes": request.timeout_minutes,
        "validation_config": request.validation_config,
        "status": "started",
        "started_at": datetime.utcnow().isoformat(),
        "timeout_at": (datetime.utcnow() + timedelta(minutes=request.timeout_minutes)).isoformat()
    }
    
    fl_rounds[round_id] = fl_round
    
    # Start background FL round process
    background_tasks.add_task(conduct_fl_round, round_id, request)
    
    logger.info(f"Started FL round {round_id} with {len(request.participants)} participants")
    
    return {
        "round_id": round_id,
        "status": "started",
        "participants": request.participants,
        "timeout_at": fl_round["timeout_at"]
    }

@app.post("/v1/fl/delta")
async def submit_model_delta(delta: ModelDeltaV1):
    """Submit model delta for FL round"""
    # Store delta
    model_deltas[delta.delta_id] = delta
    
    logger.info(f"Received model delta {delta.delta_id} from {delta.participant_id} for round {delta.round_id}")
    
    return {
        "delta_id": delta.delta_id,
        "status": "received",
        "round_id": delta.round_id,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/v1/fl/round/{round_id}")
async def get_fl_round_status(round_id: str):
    """Get FL round status"""
    if round_id not in fl_rounds:
        raise HTTPException(status_code=404, detail="FL round not found")
    
    fl_round = fl_rounds[round_id]
    
    # Get associated deltas and validations
    round_deltas = [d for d in model_deltas.values() if d.round_id == round_id]
    round_validations = [v for v in validation_results.values() 
                        if any(d.delta_id == v.delta_id for d in round_deltas)]
    
    return {
        "round": fl_round,
        "deltas_received": len(round_deltas),
        "validations": len(round_validations),
        "validation_results": [v.dict() for v in round_validations]
    }

@app.get("/v1/fl/rounds")
async def list_fl_rounds():
    """List all FL rounds"""
    return {
        "rounds": list(fl_rounds.values()),
        "total": len(fl_rounds)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "fl-orchestrator",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "active_rounds": len([r for r in fl_rounds.values() if r["status"] in ["started", "collecting_deltas", "aggregating", "storing"]])
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
    uvicorn.run(app, host="0.0.0.0", port=8003)