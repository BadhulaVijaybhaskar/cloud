from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import os, json, time, hashlib

app = FastAPI(title="Neural Fabric Scheduler", version="1.0.0")
start_time = time.time()
requests_total = Counter("nf_sched_requests_total","requests",["phase","tenant"])

SCHEDULES = {}
NODES = {}
SIM_MODE = os.getenv("SIMULATION_MODE","true").lower() == "true"

@app.get("/health")
def health():
    return {"status":"healthy","uptime":round(time.time()-start_time,2),"simulation":SIM_MODE}

@app.get("/metrics")
def metrics():
    return JSONResponse(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/node/register")
def register_node(data: dict):
    nid = data.get("node_id","node-"+hashlib.sha1(str(time.time()).encode()).hexdigest()[:6])
    NODES[nid] = {"gpus": data.get("gpus",1), "ts": time.time()}
    return {"node_id": nid, "registered": True}

@app.post("/schedule")
def schedule_job(data: dict, req: Request):
    tenant = data.get("tenant_id","anon")
    mid = data.get("model_id","m-unknown")
    job_id = hashlib.sha1(f"{tenant}-{mid}-{time.time()}".encode()).hexdigest()[:10]
    SCHEDULES[job_id] = {"tenant":tenant,"model":mid,"status":"scheduled","sim":SIM_MODE}
    requests_total.labels(phase="H.2",tenant=tenant).inc()
    return {"job_id":job_id,"status":"scheduled","simulation":SIM_MODE}

@app.get("/schedule/{jid}")
def get_schedule(jid:str):
    return SCHEDULES.get(jid,{"error":"not_found"})

@app.post("/failover/promote")
def promote(payload:dict):
    return {"action":"promote","region":payload.get("region","secondary"),"tenant":payload.get("tenant_id"),"dry_run":payload.get("dry_run",True),"ok":True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8600)