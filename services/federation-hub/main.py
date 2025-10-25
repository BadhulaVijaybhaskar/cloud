from fastapi import FastAPI
import json, os, time, uuid

app = FastAPI()

@app.post("/federation/register")
def register(payload: dict):
    # Store registration in federation_registry.json
    os.makedirs("/tmp", exist_ok=True)
    registry_file = "/tmp/federation_registry.json"
    
    # Load existing registry
    registry = []
    if os.path.exists(registry_file):
        with open(registry_file, 'r') as f:
            registry = json.load(f)
    
    # Add new registration
    registration = {
        "id": str(uuid.uuid4()),
        "node_id": payload.get("node_id", "unknown"),
        "endpoint": payload.get("endpoint", ""),
        "capabilities": payload.get("capabilities", []),
        "registered_at": time.time(),
        "status": "active"
    }
    
    registry.append(registration)
    
    # Save registry
    with open(registry_file, 'w') as f:
        json.dump(registry, f, indent=2)
    
    return {"status": "registered", "registration_id": registration["id"]}

@app.get("/federation/nodes")
def list_nodes():
    registry_file = "/tmp/federation_registry.json"
    if os.path.exists(registry_file):
        with open(registry_file, 'r') as f:
            return json.load(f)
    return []

@app.get("/health")
def health():
    return {"status": "ok", "service": "federation-hub"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8030)