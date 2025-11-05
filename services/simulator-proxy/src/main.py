#!/usr/bin/env python3
import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8804))

# Predefined scenarios for simulation
SCENARIOS = {
    "meta_proposal": {
        "description": "Test meta-proposal impact on system",
        "baseline_metrics": {"latency": 150, "cpu": 65, "memory": 70},
        "duration_minutes": 30
    },
    "traffic_spike": {
        "description": "Simulate 3x traffic increase",
        "baseline_metrics": {"latency": 120, "cpu": 45, "memory": 60},
        "duration_minutes": 15
    },
    "degradation_event": {
        "description": "Simulate service degradation",
        "baseline_metrics": {"latency": 200, "cpu": 80, "memory": 85},
        "duration_minutes": 45
    }
}

@app.route('/health')
def health():
    return jsonify({"status": "ok", "simulation_mode": SIMULATION_MODE})

@app.route('/v1/run', methods=['POST'])
def run_simulation():
    """Run synthetic scenarios to measure proposal impact"""
    data = request.get_json() or {}
    scenario_id = data.get('scenario_id', 'meta_proposal')
    overrides = data.get('overrides', {})
    
    if scenario_id not in SCENARIOS:
        return jsonify({"error": f"Unknown scenario: {scenario_id}"}), 400
    
    scenario = SCENARIOS[scenario_id].copy()
    run_id = str(uuid.uuid4())
    
    # Apply overrides to scenario
    if overrides:
        scenario.update(overrides)
    
    # Simulate running the scenario
    simulated_metrics = {
        "latency_p95": scenario["baseline_metrics"]["latency"] * 0.85,  # 15% improvement
        "cpu_avg": scenario["baseline_metrics"]["cpu"] * 1.1,  # 10% increase
        "memory_peak": scenario["baseline_metrics"]["memory"] * 0.95,  # 5% reduction
        "error_rate": 0.02,  # 2% error rate
        "throughput_rps": 1250
    }
    
    # Determine safety flags
    safety_flags = []
    if simulated_metrics["cpu_avg"] > 90:
        safety_flags.append("HIGH_CPU_RISK")
    if simulated_metrics["error_rate"] > 0.05:
        safety_flags.append("HIGH_ERROR_RATE")
    if simulated_metrics["latency_p95"] > 500:
        safety_flags.append("LATENCY_DEGRADATION")
    
    result = {
        "run_id": run_id,
        "scenario_id": scenario_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "simulation_mode": SIMULATION_MODE,
        "metrics": simulated_metrics,
        "safety_flags": safety_flags,
        "recommendation": "PROCEED" if not safety_flags else "REVIEW_REQUIRED",
        "confidence": 0.92,
        "duration_simulated_minutes": scenario.get("duration_minutes", 30)
    }
    
    # Store simulation artifacts
    os.makedirs("reports/k5", exist_ok=True)
    with open(f"reports/k5/simulation_{run_id}.json", 'w') as f:
        json.dump(result, f, indent=2)
    
    return jsonify(result)

@app.route('/v1/scenarios')
def list_scenarios():
    """List available simulation scenarios"""
    return jsonify({
        "scenarios": SCENARIOS,
        "count": len(SCENARIOS)
    })

@app.route('/v1/runs')
def list_runs():
    """List simulation runs"""
    runs = []
    reports_dir = "reports/k5"
    if os.path.exists(reports_dir):
        for f in os.listdir(reports_dir):
            if f.startswith("simulation_") and f.endswith(".json"):
                try:
                    with open(os.path.join(reports_dir, f)) as file:
                        runs.append(json.load(file))
                except:
                    continue
    
    return jsonify({"runs": runs, "count": len(runs)})

if __name__ == '__main__':
    print(f"Starting Simulator Proxy on port {SERVICE_PORT} (simulation={SIMULATION_MODE})")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)