# ============================================
# I.8.2 scenario-builder/main.py
# ============================================
from fastapi import FastAPI, Request
import os, json, uuid, logging
app = FastAPI(title="Scenario Builder", version="1.0.0")
logging.basicConfig(level=logging.INFO)
SCENARIOS = {}

@app.get("/health")
async def health(): return {"status":"healthy"}

@app.get("/metrics")
async def metrics(): return {"scenarios":len(SCENARIOS)}

@app.post("/scenarios")
async def create_scenario(req: Request):
    data = await req.json()
    sid = data.get("scenario_id", str(uuid.uuid4()))
    SCENARIOS[sid]=data
    os.makedirs("scenarios", exist_ok=True)
    open(f"scenarios/{sid}.json","w").write(json.dumps(data,indent=2))
    return {"scenario_id":sid,"status":"saved"}

@app.get("/scenarios/{sid}")
async def get_scenario(sid:str):
    return SCENARIOS.get(sid,{"error":"not_found"})

@app.post("/scenarios/{sid}/validate")
async def validate_scenario(sid:str):
    if sid not in SCENARIOS: return {"status":"missing"}
    s=SCENARIOS[sid]
    required=["actors","duration_seconds"]
    missing=[r for r in required if r not in s]
    return {"status":"valid" if not missing else "invalid","missing":missing}

if __name__=="__main__":
    import uvicorn; uvicorn.run(app,host="0.0.0.0",port=9802)