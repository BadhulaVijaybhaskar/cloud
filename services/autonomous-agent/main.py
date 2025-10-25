from fastapi import FastAPI, BackgroundTasks
import yaml, os, uuid, logging
from prometheus_client import Counter

app = FastAPI()
RUNS = Counter("autonomous_agent_runs_total", "Total runs")

@app.post("/agent/run")
def run(payload: dict, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())
    background_tasks.add_task(process, run_id, payload)
    return {"run_id": run_id}

@app.get("/agent/status/{run_id}")
def status(run_id: str):
    # Check if run file exists
    import os
    run_file = f"/tmp/agent_runs/{run_id}.json"
    if os.path.exists(run_file):
        import json
        with open(run_file, "r") as f:
            return json.load(f)
    return {"error": "Run not found"}

def process(run_id, payload):
    RUNS.inc()
    # observe -> decide -> act stages (simulate)
    import json, os, time
    os.makedirs("/tmp/agent_runs", exist_ok=True)
    
    # Simulate agent reasoning
    result = {
        "id": run_id, 
        "payload": payload, 
        "stages": {
            "observe": {"status": "completed", "data_sources": ["prometheus", "insight-stream"]},
            "decide": {"status": "completed", "decision": "no_action_needed", "confidence": 0.85},
            "act": {"status": "skipped", "reason": "safety_mode_manual"}
        },
        "result": "simulated", 
        "ts": time.time()
    }
    
    with open(f"/tmp/agent_runs/{run_id}.json", "w") as f:
        json.dump(result, f)

@app.get("/health")
def health():
    return {"status": "ok", "mode": "simulation"}

@app.get("/metrics")
def metrics():
    from prometheus_client import generate_latest
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8020)