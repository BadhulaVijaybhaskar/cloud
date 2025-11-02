# ============================================
# I.8.4 behavior-analyzer/main.py
# ============================================
from fastapi import FastAPI, Request
import os, json, random, logging
app = FastAPI(title="Behavior Analyzer", version="1.0.0")
logging.basicConfig(level=logging.INFO)

@app.get("/health")
async def health(): return {"status":"healthy"}

@app.get("/metrics")
async def metrics(): return {"last_analysis_score": random.random()}

@app.post("/analyze")
async def analyze(req: Request):
    body = await req.json()
    score = round(random.uniform(0.7,0.99),3)
    response = {"behavior_score":score,"bias_warnings":random.randint(0,3),"explainable_events":random.randint(90,100)}
    os.makedirs("reports", exist_ok=True)
    open("reports/I.8_behavior_report.json","w").write(json.dumps(response,indent=2))
    return response

if __name__=="__main__":
    import uvicorn; uvicorn.run(app,host="0.0.0.0",port=9804)