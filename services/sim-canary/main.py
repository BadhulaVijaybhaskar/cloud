#!/usr/bin/env python3
"""
Phase I.4.7 - Simulation & Canary Runner
Replay decisions, dry-run validations, canary rollouts and rollback tests
"""

import os
import json
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
CANARY_RUNS_TOTAL = Counter('canary_runs_total', 'Total canary runs executed')
SIMULATIONS_TOTAL = Counter('simulations_total', 'Total simulations executed')
CANARY_SUCCESS_RATE = Histogram('canary_success_rate', 'Canary success rate distribution')

app = FastAPI(title="Simulation & Canary Runner", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

# In-memory storage for simulation
canary_runs = {}
simulation_results = {}

class CanaryRequest(BaseModel):
    proposal_id: str
    manifest: Dict[str, Any]
    canary_percentage: Optional[float] = 10.0
    rollback_threshold: Optional[float] = 0.05  # 5% error rate threshold
    duration_minutes: Optional[int] = 30

class SimulationRequest(BaseModel):
    proposal_id: str
    manifest: Dict[str, Any]
    replay_count: Optional[int] = 100
    scenario: Optional[str] = "normal"  # normal, stress, failure

class ValidationResult(BaseModel):
    passed: bool
    score: float
    details: Dict[str, Any]
    recommendations: List[str]

def simulate_canary_metrics(action: str, target: str, percentage: float, duration: int) -> Dict[str, Any]:
    """Simulate canary deployment metrics"""
    # Base success rates by action type
    action_success_rates = {
        "scale_up": 0.92,
        "scale_down": 0.88,
        "security_patch": 0.95,
        "update_config": 0.85,
        "restart_service": 0.80,
        "deploy_new": 0.75
    }
    
    base_success_rate = action_success_rates.get(action, 0.85)
    
    # Adjust for canary percentage (smaller canaries are safer)
    canary_factor = 1.0 - (percentage / 100.0) * 0.1
    success_rate = min(base_success_rate * canary_factor, 1.0)
    
    # Generate metrics with some randomness
    error_rate = 1.0 - success_rate + random.uniform(-0.02, 0.02)
    error_rate = max(0.0, min(error_rate, 1.0))
    
    response_time_ms = random.uniform(100, 500) * (1 + error_rate)
    throughput_rps = random.uniform(800, 1200) * (1 - error_rate * 0.5)
    
    return {
        "success_rate": round(success_rate, 4),
        "error_rate": round(error_rate, 4),
        "response_time_p95_ms": round(response_time_ms, 2),
        "throughput_rps": round(throughput_rps, 2),
        "cpu_utilization": round(random.uniform(30, 80), 2),
        "memory_utilization": round(random.uniform(40, 85), 2),
        "network_errors": random.randint(0, 5),
        "timeout_count": random.randint(0, 3)
    }

async def run_canary_deployment(canary_id: str, request: CanaryRequest):
    """Execute canary deployment with monitoring"""
    try:
        canary = canary_runs[canary_id]
        action = request.manifest.get('action', 'unknown')
        target = request.manifest.get('target', 'system')
        
        logger.info(f"Starting canary {canary_id} for {action} on {target}")
        
        # Simulate canary deployment phases
        phases = ["initializing", "deploying", "monitoring", "evaluating"]
        
        for phase in phases:
            canary["status"] = phase
            canary["current_phase"] = phase
            
            # Simulate phase duration
            phase_duration = request.duration_minutes / len(phases)
            await asyncio.sleep(min(phase_duration * 60, 30))  # Cap at 30 seconds for simulation
            
            # Generate metrics for this phase
            metrics = simulate_canary_metrics(action, target, request.canary_percentage, request.duration_minutes)
            canary["metrics"] = metrics
            
            # Check rollback threshold
            if metrics["error_rate"] > request.rollback_threshold:
                canary["status"] = "rollback_triggered"
                canary["recommendation"] = "rollback"
                canary["rollback_reason"] = f"Error rate {metrics['error_rate']:.4f} exceeds threshold {request.rollback_threshold}"
                logger.warning(f"Canary {canary_id} triggered rollback due to high error rate")
                break
        
        # Final evaluation
        if canary["status"] != "rollback_triggered":
            final_metrics = canary["metrics"]
            if final_metrics["error_rate"] <= request.rollback_threshold and final_metrics["success_rate"] >= 0.95:
                canary["status"] = "success"
                canary["recommendation"] = "proceed"
            else:
                canary["status"] = "failed"
                canary["recommendation"] = "investigate"
        
        canary["completed_at"] = datetime.utcnow().isoformat()
        CANARY_SUCCESS_RATE.observe(canary["metrics"]["success_rate"])
        
        logger.info(f"Canary {canary_id} completed with status: {canary['status']}")
        
    except Exception as e:
        logger.error(f"Error in canary deployment {canary_id}: {e}")
        canary["status"] = "error"
        canary["error"] = str(e)

def run_decision_simulation(proposal_id: str, manifest: Dict[str, Any], scenario: str, replay_count: int) -> Dict[str, Any]:
    """Run decision simulation with multiple replays"""
    action = manifest.get('action', 'unknown')
    target = manifest.get('target', 'system')
    
    # Scenario-based success rate adjustments
    scenario_factors = {
        "normal": 1.0,
        "stress": 0.85,
        "failure": 0.60,
        "peak_load": 0.80,
        "network_partition": 0.70
    }
    
    base_factor = scenario_factors.get(scenario, 1.0)
    
    # Run multiple simulations
    results = []
    for i in range(replay_count):
        # Simulate individual run
        success = random.random() < (0.9 * base_factor)
        duration = random.uniform(30, 300)  # 30 seconds to 5 minutes
        
        result = {
            "run_id": i + 1,
            "success": success,
            "duration_seconds": round(duration, 2),
            "error_code": None if success else random.choice(["TIMEOUT", "RESOURCE_ERROR", "VALIDATION_FAILED"]),
            "metrics": simulate_canary_metrics(action, target, 100.0, 5) if success else None
        }
        results.append(result)
    
    # Aggregate results
    successful_runs = [r for r in results if r["success"]]
    success_rate = len(successful_runs) / len(results)
    avg_duration = sum(r["duration_seconds"] for r in successful_runs) / max(len(successful_runs), 1)
    
    return {
        "total_runs": replay_count,
        "successful_runs": len(successful_runs),
        "success_rate": round(success_rate, 4),
        "average_duration": round(avg_duration, 2),
        "scenario": scenario,
        "results": results[:10],  # Return first 10 detailed results
        "recommendation": "proceed" if success_rate >= 0.95 else "investigate" if success_rate >= 0.80 else "reject"
    }

@app.post("/canary/start")
async def start_canary_deployment(
    request: CanaryRequest,
    background_tasks: BackgroundTasks
):
    """Start canary deployment for proposal"""
    CANARY_RUNS_TOTAL.inc()
    
    # Generate canary ID
    canary_id = f"canary-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{len(canary_runs)}"
    
    # Create canary run record
    canary_run = {
        "canary_id": canary_id,
        "proposal_id": request.proposal_id,
        "status": "starting",
        "canary_percentage": request.canary_percentage,
        "rollback_threshold": request.rollback_threshold,
        "duration_minutes": request.duration_minutes,
        "started_at": datetime.utcnow().isoformat(),
        "manifest": request.manifest,
        "metrics": {},
        "recommendation": None
    }
    
    canary_runs[canary_id] = canary_run
    
    # Start background canary process
    background_tasks.add_task(run_canary_deployment, canary_id, request)
    
    return {
        "canary_id": canary_id,
        "status": "starting",
        "canary_percentage": request.canary_percentage,
        "estimated_completion": (datetime.utcnow() + timedelta(minutes=request.duration_minutes)).isoformat()
    }

@app.get("/canary/{canary_id}")
async def get_canary_status(canary_id: str):
    """Get canary deployment status and metrics"""
    if canary_id not in canary_runs:
        raise HTTPException(status_code=404, detail="Canary run not found")
    
    return canary_runs[canary_id]

@app.post("/simulate")
async def run_simulation(request: SimulationRequest):
    """Run decision simulation with replay"""
    SIMULATIONS_TOTAL.inc()
    
    # Generate simulation ID
    simulation_id = f"sim-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{len(simulation_results)}"
    
    # Run simulation
    simulation_result = run_decision_simulation(
        request.proposal_id,
        request.manifest,
        request.scenario,
        request.replay_count
    )
    
    # Store results
    simulation_record = {
        "simulation_id": simulation_id,
        "proposal_id": request.proposal_id,
        "manifest": request.manifest,
        "scenario": request.scenario,
        "replay_count": request.replay_count,
        "results": simulation_result,
        "created_at": datetime.utcnow().isoformat()
    }
    
    simulation_results[simulation_id] = simulation_record
    
    logger.info(f"Completed simulation {simulation_id} with {simulation_result['success_rate']:.2%} success rate")
    
    return {
        "simulation_id": simulation_id,
        "results": simulation_result
    }

@app.post("/validate")
async def validate_proposal(proposal_id: str, manifest: Dict[str, Any]):
    """Validate proposal through dry-run checks"""
    validation_checks = []
    
    # Check 1: Manifest structure
    required_fields = ["action", "target"]
    missing_fields = [field for field in required_fields if field not in manifest]
    
    validation_checks.append({
        "check": "manifest_structure",
        "passed": len(missing_fields) == 0,
        "details": {"missing_fields": missing_fields} if missing_fields else {"status": "valid"}
    })
    
    # Check 2: Action safety
    risky_actions = ["delete", "destroy", "terminate"]
    action = manifest.get("action", "")
    is_risky = action in risky_actions
    
    validation_checks.append({
        "check": "action_safety",
        "passed": not is_risky or manifest.get("approval_required", False),
        "details": {"risky_action": is_risky, "approval_required": manifest.get("approval_required", False)}
    })
    
    # Check 3: Rollback capability
    has_rollback = manifest.get("rollback_plan", False)
    validation_checks.append({
        "check": "rollback_capability",
        "passed": has_rollback,
        "details": {"rollback_plan_present": has_rollback}
    })
    
    # Calculate overall score
    passed_checks = sum(1 for check in validation_checks if check["passed"])
    score = passed_checks / len(validation_checks)
    
    # Generate recommendations
    recommendations = []
    if not validation_checks[0]["passed"]:
        recommendations.append("Add required fields to manifest")
    if not validation_checks[1]["passed"]:
        recommendations.append("Add approval requirement for risky actions")
    if not validation_checks[2]["passed"]:
        recommendations.append("Include rollback plan for safety")
    
    return ValidationResult(
        passed=score >= 0.8,
        score=score,
        details={"checks": validation_checks},
        recommendations=recommendations
    )

@app.get("/health")
async def health_check():
    """Health check endpoint (P4)"""
    return {
        "status": "healthy",
        "service": "sim-canary",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "active_canaries": len([c for c in canary_runs.values() if c["status"] in ["starting", "deploying", "monitoring"]]),
        "completed_simulations": len(simulation_results)
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
    uvicorn.run(app, host="0.0.0.0", port=9207)