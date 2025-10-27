from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime

app = FastAPI(title="ATOM Audit Pipeline", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class AuditEntry(BaseModel):
    service: str
    operation: str
    user_id: str = ""
    metadata: dict = {}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "audit-pipeline", "simulation": SIMULATION_MODE}

@app.post("/audit")
def log_audit_entry(entry: AuditEntry):
    """Log immutable audit entry"""
    audit_record = {
        "id": hashlib.sha256(f"{entry.service}{entry.operation}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
        "timestamp": datetime.now().isoformat(),
        "service": entry.service,
        "operation": entry.operation,
        "user_hash": hashlib.sha256(entry.user_id.encode()).hexdigest()[:16] if entry.user_id else "",
        "metadata_hash": hashlib.sha256(json.dumps(entry.metadata, sort_keys=True).encode()).hexdigest()[:16]
    }
    
    print(f"AUDIT_RECORD: {json.dumps(audit_record)}")
    return {"status": "logged", "audit_id": audit_record["id"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8303)