from fastapi import FastAPI, BackgroundTasks
from prometheus_client import Counter, generate_latest
import os, yaml, asyncio

app = FastAPI()
INGESTED = Counter("insight_ingested_total", "ingested messages")

# load config
cfg_path = os.getenv("INSIGHT_CONFIG", "config.example.yaml")
with open(cfg_path) as f:
    cfg = yaml.safe_load(f)

BACKEND = cfg.get("ingestion", {}).get("backend", "mock")

@app.get("/health")
def health():
    return {"status": "ok", "backend": BACKEND}

@app.get("/metrics")
def metrics():
    return generate_latest()

@app.post("/ingest")
async def ingest(payload: dict, background_tasks: BackgroundTasks):
    # quick handler: increment counter and enqueue to backend
    INGESTED.inc()
    background_tasks.add_task(process, payload)
    return {"status": "accepted"}

async def process(payload):
    # push to backend or simulate
    if BACKEND == "mock":
        await asyncio.sleep(0.01)
        return True
    # real backend hooks left for implementation

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.insight-stream.main:app", host="0.0.0.0", port=8010, log_level="info")