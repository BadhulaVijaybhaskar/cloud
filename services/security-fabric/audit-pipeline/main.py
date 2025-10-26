from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

app = FastAPI(title="ATOM Audit Pipeline", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
AUDIT_LEDGER_PATH = "reports/logs/audit_ledger.jsonl"

class AuditEvent(BaseModel):
    action: str
    actor: Optional[str] = "system"
    tenant: Optional[str] = "default"
    resource: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

events_processed = 0
ledger_size = 0

def append_to_ledger(event_data: Dict[str, Any]) -> str:
    global events_processed, ledger_size
    
    # Create immutable audit entry
    timestamp = datetime.utcnow().isoformat()
    sequence_id = events_processed + 1
    
    audit_entry = {
        "sequence_id": sequence_id,
        "timestamp": timestamp,
        "action": event_data["action"],
        "actor": event_data.get("actor", "system"),
        "tenant": event_data.get("tenant", "default"),
        "resource": event_data.get("resource"),
        "metadata": event_data.get("metadata", {}),
        "source_service": "audit-pipeline"
    }
    
    # Calculate hash for integrity
    entry_json = json.dumps(audit_entry, sort_keys=True)
    audit_entry["sha256"] = hashlib.sha256(entry_json.encode()).hexdigest()
    
    # Append to ledger (JSONL format for immutability)
    os.makedirs(os.path.dirname(AUDIT_LEDGER_PATH), exist_ok=True)
    with open(AUDIT_LEDGER_PATH, "a") as f:
        f.write(json.dumps(audit_entry) + "\n")
    
    events_processed += 1
    ledger_size = os.path.getsize(AUDIT_LEDGER_PATH) if os.path.exists(AUDIT_LEDGER_PATH) else 0
    
    return audit_entry["sha256"]

@app.get("/health")
async def health():
    ledger_exists = os.path.exists(AUDIT_LEDGER_PATH)
    
    return {
        "status": "ok",
        "service": "audit-pipeline",
        "env": "SIM" if SIMULATION_MODE else "LIVE",
        "ledger_exists": ledger_exists,
        "events_processed": events_processed,
        "ledger_size_bytes": ledger_size,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/append")
async def append_audit_event(event: AuditEvent):
    try:
        # Validate required fields
        if not event.action:
            raise HTTPException(status_code=400, detail="Action is required")
        
        event_data = {
            "action": event.action,
            "actor": event.actor,
            "tenant": event.tenant,
            "resource": event.resource,
            "metadata": event.metadata or {}
        }
        
        # Append to immutable ledger
        entry_hash = append_to_ledger(event_data)
        
        return {
            "status": "appended",
            "sequence_id": events_processed,
            "entry_hash": entry_hash,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to append audit event: {str(e)}")

@app.get("/export")
async def export_ledger(limit: Optional[int] = None, format: str = "json"):
    try:
        if not os.path.exists(AUDIT_LEDGER_PATH):
            return {
                "entries": [],
                "count": 0,
                "format": format,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        entries = []
        with open(AUDIT_LEDGER_PATH, "r") as f:
            lines = f.readlines()
            
            # Apply limit if specified
            if limit:
                lines = lines[-limit:]
            
            for line in lines:
                try:
                    entry = json.loads(line.strip())
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        if format == "csv":
            # Convert to CSV format for compliance reports
            csv_data = "sequence_id,timestamp,action,actor,tenant,resource,sha256\n"
            for entry in entries:
                csv_data += f"{entry.get('sequence_id', '')},{entry.get('timestamp', '')},{entry.get('action', '')},{entry.get('actor', '')},{entry.get('tenant', '')},{entry.get('resource', '')},{entry.get('sha256', '')}\n"
            
            return {
                "format": "csv",
                "data": csv_data,
                "count": len(entries),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "entries": entries,
            "count": len(entries),
            "format": format,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export ledger: {str(e)}")

@app.get("/verify")
async def verify_ledger_integrity():
    try:
        if not os.path.exists(AUDIT_LEDGER_PATH):
            return {
                "valid": True,
                "entries_verified": 0,
                "corrupted_entries": [],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        corrupted_entries = []
        entries_verified = 0
        
        with open(AUDIT_LEDGER_PATH, "r") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    
                    # Verify hash integrity
                    stored_hash = entry.pop("sha256", None)
                    calculated_hash = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
                    
                    if stored_hash != calculated_hash:
                        corrupted_entries.append({
                            "line": line_num,
                            "sequence_id": entry.get("sequence_id"),
                            "expected_hash": calculated_hash,
                            "stored_hash": stored_hash
                        })
                    
                    entries_verified += 1
                    
                except json.JSONDecodeError:
                    corrupted_entries.append({
                        "line": line_num,
                        "error": "Invalid JSON"
                    })
        
        return {
            "valid": len(corrupted_entries) == 0,
            "entries_verified": entries_verified,
            "corrupted_entries": corrupted_entries,
            "corruption_rate": len(corrupted_entries) / entries_verified if entries_verified > 0 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify ledger: {str(e)}")

@app.get("/search")
async def search_audit_logs(
    action: Optional[str] = None,
    actor: Optional[str] = None,
    tenant: Optional[str] = None,
    limit: int = 100
):
    try:
        if not os.path.exists(AUDIT_LEDGER_PATH):
            return {
                "entries": [],
                "count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        matching_entries = []
        
        with open(AUDIT_LEDGER_PATH, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Apply filters
                    if action and action.lower() not in entry.get("action", "").lower():
                        continue
                    if actor and actor.lower() not in entry.get("actor", "").lower():
                        continue
                    if tenant and tenant != entry.get("tenant"):
                        continue
                    
                    matching_entries.append(entry)
                    
                    if len(matching_entries) >= limit:
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        return {
            "entries": matching_entries,
            "count": len(matching_entries),
            "filters": {
                "action": action,
                "actor": actor,
                "tenant": tenant
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search audit logs: {str(e)}")

@app.get("/metrics")
async def metrics():
    return f"""# HELP audit_pipeline_events_total Total number of audit events processed
# TYPE audit_pipeline_events_total counter
audit_pipeline_events_total {events_processed}

# HELP audit_pipeline_ledger_size_bytes Size of audit ledger in bytes
# TYPE audit_pipeline_ledger_size_bytes gauge
audit_pipeline_ledger_size_bytes {ledger_size}

# HELP audit_pipeline_ledger_entries Number of entries in ledger
# TYPE audit_pipeline_ledger_entries gauge
audit_pipeline_ledger_entries {events_processed}
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8104)