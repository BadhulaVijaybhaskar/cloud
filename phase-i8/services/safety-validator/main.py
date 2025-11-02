# ============================================
# I.8.3 safety-validator/main.py
# ============================================
from fastapi import FastAPI, Request
import os, json, logging
app = FastAPI(title="Safety Validator", version="1.0.0")
logging.basicConfig(level=logging.INFO)
POLICIES = ["P1","P2","P3","P4","P5","P6","P7","P13","P14","P15"]

@app.get("/health")
async def health(): return {"status":"healthy"}

@app.get("/metrics")
async def metrics(): return {"policies_active":len(POLICIES)}

@app.post("/validate/event")
async def validate_event(req: Request):
    event = await req.json()
    if "pii" in json.dumps(event).lower():
        result={"result":"fail","reason":"PII detected","policy":"P1"}
    elif "red_team" in json.dumps(event).lower():
        result={"result":"warn","reason":"adversarial behavior","policy":"P14"}
    else:
        result={"result":"pass"}
    logging.info(f"Validated event: {result}")
    return result

if __name__=="__main__":
    import uvicorn; uvicorn.run(app,host="0.0.0.0",port=9803)