# ============================================
# I.8.5 resilience-orchestrator/main.py
# ============================================
from fastapi import FastAPI, Request
import os, json, logging, time
app = FastAPI(title="Resilience Orchestrator", version="1.0.0")
logging.basicConfig(level=logging.INFO)
ACTIVE_FAULTS = {}

@app.get("/health")
async def health(): return {"status":"healthy","faults_active":len(ACTIVE_FAULTS)}

@app.get("/metrics")
async def metrics(): return {"faults_active":len(ACTIVE_FAULTS)}

@app.post("/inject")
async def inject(req: Request):
    data = await req.json()
    fault_id = f"fault-{len(ACTIVE_FAULTS)+1}"
    ACTIVE_FAULTS[fault_id]=data
    logging.warning(f"Injected fault {fault_id}: {data}")
    time.sleep(0.2)
    return {"fault_id":fault_id,"status":"injected"}

@app.post("/rollback")
async def rollback(req: Request):
    data = await req.json()
    fid = data.get("fault_id")
    if fid in ACTIVE_FAULTS: del ACTIVE_FAULTS[fid]
    logging.info(f"Rolled back {fid}")
    return {"status":"rolled_back","fault_id":fid}

if __name__=="__main__":
    import uvicorn; uvicorn.run(app,host="0.0.0.0",port=9805)