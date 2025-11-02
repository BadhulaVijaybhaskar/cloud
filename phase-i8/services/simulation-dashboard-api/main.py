# ============================================
# I.8.6 simulation-dashboard-api/main.py
# ============================================
from fastapi import FastAPI
import os, json, glob
app = FastAPI(title="Simulation Dashboard API", version="1.0.0")

@app.get("/health")
async def health(): return {"status":"healthy"}

@app.get("/metrics")
async def metrics(): return {"report_files":len(glob.glob('reports/*.json'))}

@app.get("/runs")
async def list_runs():
    runs = [f for f in glob.glob('reports/I.8_*.json')]
    return {"runs":runs}

@app.get("/runs/{rid}/summary")
async def run_summary(rid:str):
    path = f"reports/{rid}.json"
    if os.path.exists(path):
        return json.load(open(path))
    return {"error":"not_found"}

if __name__=="__main__":
    import uvicorn; uvicorn.run(app,host="0.0.0.0",port=9806)