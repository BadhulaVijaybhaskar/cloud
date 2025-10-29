from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime
import random

app = FastAPI(title="ATOM Resilience Simulator", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class ChaosTest(BaseModel):
    test_type: str  # "failover", "latency", "resource_exhaustion"
    target_service: str
    duration_seconds: int = 60

@app.get("/health")
def health():
    return {"status": "healthy", "service": "resilience-simulator", "simulation": SIMULATION_MODE}

@app.post("/chaos/test")
def run_chaos_test(test: ChaosTest):
    """Run chaos engineering test"""
    if SIMULATION_MODE:
        # Simulate chaos test execution
        test_results = {
            "test_id": f"chaos_{test.test_type}_{datetime.now().strftime('%H%M%S')}",
            "test_type": test.test_type,
            "target_service": test.target_service,
            "duration_seconds": test.duration_seconds,
            "status": "completed",
            "started_at": datetime.now().isoformat(),
            "results": {}
        }
        
        if test.test_type == "failover":
            test_results["results"] = {
                "failover_time_ms": random.randint(500, 1500),
                "data_loss": False,
                "recovery_successful": True,
                "p7_compliant": True
            }
        elif test.test_type == "latency":
            test_results["results"] = {
                "baseline_latency_ms": 200,
                "degraded_latency_ms": 800,
                "recovery_time_ms": 300,
                "p6_maintained": True
            }
        elif test.test_type == "resource_exhaustion":
            test_results["results"] = {
                "cpu_threshold_reached": True,
                "memory_threshold_reached": True,
                "graceful_degradation": True,
                "service_availability": 0.95
            }
        
        return test_results
    
    return {"error": "Chaos testing unavailable"}

@app.get("/chaos/scenarios")
def list_chaos_scenarios():
    """List available chaos scenarios"""
    if SIMULATION_MODE:
        return {
            "scenarios": [
                {"name": "neural_fabric_failover", "description": "Test neural fabric failover"},
                {"name": "quantum_backend_failure", "description": "Simulate quantum backend failure"},
                {"name": "hybrid_coordinator_overload", "description": "Test coordinator under load"},
                {"name": "network_partition", "description": "Simulate network partition"},
                {"name": "pqc_key_rotation_failure", "description": "Test PQC key rotation failure"}
            ]
        }
    
    return {"error": "Scenario listing unavailable"}

@app.get("/chaos/reports")
def get_resilience_reports():
    """Get resilience test reports"""
    if SIMULATION_MODE:
        return {
            "total_tests_run": 25,
            "success_rate": 0.92,
            "avg_recovery_time_ms": 850,
            "p7_compliance_rate": 0.96,
            "critical_failures": 0,
            "last_test": datetime.now().isoformat()
        }
    
    return {"error": "Reports unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8705)