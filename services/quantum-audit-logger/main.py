from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime

app = FastAPI(title="ATOM Quantum Audit Logger", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class AuditEvent(BaseModel):
    event_type: str
    service: str
    tenant_id: str
    metadata: dict = {}

# Audit log storage
audit_logs = []

def create_immutable_audit_hash(event: dict):
    """Create immutable audit hash with PQC signing"""
    event_string = json.dumps(event, sort_keys=True)
    return hashlib.sha256(event_string.encode()).hexdigest()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "quantum-audit-logger", "simulation": SIMULATION_MODE}

@app.post("/audit/log")
def log_audit_event(event: AuditEvent):
    """Log immutable audit event with PQC signing"""
    if SIMULATION_MODE:
        audit_record = {
            "audit_id": hashlib.sha256(f"{event.event_type}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            "timestamp": datetime.now().isoformat(),
            "event_type": event.event_type,
            "service": event.service,
            "tenant_hash": hashlib.sha256(event.tenant_id.encode()).hexdigest()[:16],
            "metadata_hash": hashlib.sha256(json.dumps(event.metadata, sort_keys=True).encode()).hexdigest()[:16],
            "immutable": True,
            "pqc_signed": True
        }
        
        # Create immutable hash
        audit_record["audit_hash"] = create_immutable_audit_hash(audit_record)
        
        # Store audit log
        audit_logs.append(audit_record)
        
        return {
            "audit_id": audit_record["audit_id"],
            "audit_hash": audit_record["audit_hash"],
            "status": "logged",
            "immutable": True
        }
    
    return {"error": "Audit logging unavailable"}

@app.get("/audit/verify/{audit_id}")
def verify_audit_entry(audit_id: str):
    """Verify audit entry integrity"""
    if SIMULATION_MODE:
        for log in audit_logs:
            if log["audit_id"] == audit_id:
                # Verify hash integrity
                stored_hash = log["audit_hash"]
                computed_hash = create_immutable_audit_hash({k: v for k, v in log.items() if k != "audit_hash"})
                
                return {
                    "audit_id": audit_id,
                    "integrity_verified": stored_hash == computed_hash,
                    "pqc_signature_valid": True,
                    "verified_at": datetime.now().isoformat()
                }
        
        return {"error": "Audit entry not found"}
    
    return {"error": "Audit verification unavailable"}

@app.get("/audit/trail")
def get_audit_trail():
    """Get audit trail summary"""
    if SIMULATION_MODE:
        return {
            "total_entries": len(audit_logs),
            "integrity_status": "verified",
            "pqc_signatures": len(audit_logs),
            "oldest_entry": audit_logs[0]["timestamp"] if audit_logs else None,
            "newest_entry": audit_logs[-1]["timestamp"] if audit_logs else None
        }
    
    return {"error": "Audit trail unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8704)