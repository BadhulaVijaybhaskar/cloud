from fastapi import FastAPI
import json, time, uuid, random

app = FastAPI()

@app.post("/chaos/schedule")
def schedule_chaos(payload: dict):
    chaos_id = str(uuid.uuid4())
    chaos_event = {
        "id": chaos_id,
        "type": payload.get("type", "cpu_spike"),
        "target": payload.get("target", "random_pod"),
        "duration": payload.get("duration", 60),
        "scheduled_at": time.time(),
        "status": "scheduled"
    }
    
    # Simulate chaos injection
    result = inject_chaos(chaos_event)
    return {"chaos_id": chaos_id, "result": result}

def inject_chaos(event):
    """Simulate chaos injection"""
    chaos_type = event["type"]
    if chaos_type == "cpu_spike":
        return {"status": "injected", "message": "CPU spike simulated"}
    elif chaos_type == "network_delay":
        return {"status": "injected", "message": "Network delay simulated"}
    elif chaos_type == "pod_kill":
        return {"status": "injected", "message": "Pod termination simulated"}
    else:
        return {"status": "unknown", "message": "Unknown chaos type"}

@app.get("/chaos/status/{chaos_id}")
def get_chaos_status(chaos_id: str):
    return {"id": chaos_id, "status": "completed", "recovery_validated": True}

@app.get("/health")
def health():
    return {"status": "ok", "service": "chaos-orchestrator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8040)