# ============================================
# I.8.1 simulation-engine/main.py
# ============================================
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os, time, json, uuid, logging

app = FastAPI(title="Simulation Engine", version="1.0.0")
logger = logging.getLogger("simulation-engine")
logging.basicConfig(level=logging.INFO)

SIM_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
RUNS = {}

@app.get("/health")
async def health():
    return {"status":"healthy","simulation_mode":SIM_MODE}

@app.get("/metrics")
async def metrics():
    return {"runs_total": len(RUNS), "active_runs": sum(r["status"]=="running" for r in RUNS.values())}

@app.post("/run")
async def run_scenario(request: Request):
    body = await request.json()
    run_id = body.get("scenario_id", str(uuid.uuid4()))
    RUNS[run_id] = {"status":"running","started":time.time(),"body":body}
    logger.info(f"Started simulation {run_id}")
    time.sleep(0.5 if SIM_MODE else 0.1)
    RUNS[run_id]["status"]="completed"
    RUNS[run_id]["ended"]=time.time()
    return {"run_id":run_id,"status":"completed"}

@app.get("/status/{run_id}")
async def get_status(run_id:str):
    return RUNS.get(run_id,{"error":"not_found"})

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=9801)