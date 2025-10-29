#!/usr/bin/env python3
"""
Phase I.4.6 - Decision Auditor
Immutable trace store with PQC signatures and rollback helpers
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
AUDIT_ENTRIES_TOTAL = Counter('audit_entries_total', 'Total audit entries created')
SNAPSHOTS_TOTAL = Counter('snapshots_total', 'Total state snapshots stored')
AUDIT_QUERIES = Counter('audit_queries_total', 'Total audit queries')

app = FastAPI(title="Decision Auditor", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

# In-memory storage for simulation
audit_trail = {}
state_snapshots = {}
rollback_plans = {}

class SnapshotRequest(BaseModel):
    proposal_id: str
    snapshot_type: str  # 'pre', 'post'
    state_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}

class RollbackRequest(BaseModel):
    proposal_id: str
    target_snapshot_id: str
    dry_run: bool = True
    steps: Optional[List[Dict[str, Any]]] = []

def generate_pqc_signature(data: Dict[str, Any]) -> str:
    """Generate Post-Quantum Cryptography signature simulation"""
    if SIMULATION_MODE:
        # Simulate PQC signature (e.g., CRYSTALS-Dilithium)
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.sha256(data_str.encode())
        return f"pqc-dilithium-{hash_obj.hexdigest()[:32]}"
    # In production: actual PQC signature
    return "production-pqc-signature"

def calculate_audit_hash(audit_entry: Dict[str, Any]) -> str:
    """Calculate SHA256 hash for audit entry integrity"""
    # Remove hash field if present to avoid circular reference
    entry_copy = audit_entry.copy()
    entry_copy.pop('audit_hash', None)
    entry_str = json.dumps(entry_copy, sort_keys=True)
    return hashlib.sha256(entry_str.encode()).hexdigest()

def redact_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Redact sensitive data from audit entries (P1)"""
    sensitive_keys = ['password', 'secret', 'token', 'key', 'credential', 'pii']
    
    def redact_recursive(obj):
        if isinstance(obj, dict):
            return {
                k: '<REDACTED>' if any(sens in k.lower() for sens in sensitive_keys)
                else redact_recursive(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [redact_recursive(item) for item in obj]
        return obj
    
    return redact_recursive(data)

@app.get("/audit/{proposal_id}")
async def get_audit_trail(proposal_id: str):
    """Get full audit trail for proposal (no raw secrets or PII)"""
    AUDIT_QUERIES.inc()
    
    if proposal_id not in audit_trail:
        raise HTTPException(status_code=404, detail="Audit trail not found")
    
    # Get all audit entries for this proposal
    entries = audit_trail[proposal_id]
    
    # Redact sensitive information
    redacted_entries = [redact_sensitive_data(entry) for entry in entries]
    
    return {
        "proposal_id": proposal_id,
        "audit_entries": redacted_entries,
        "total_entries": len(redacted_entries),
        "integrity_verified": all(
            entry.get('audit_hash') == calculate_audit_hash({k: v for k, v in entry.items() if k != 'audit_hash'})
            for entry in entries
        )
    }

@app.post("/snapshot/{proposal_id}")
async def store_snapshot(proposal_id: str, request: SnapshotRequest):
    """Store pre/post snapshot hash references"""
    SNAPSHOTS_TOTAL.inc()
    
    # Generate snapshot ID
    snapshot_id = f"snap-{proposal_id}-{request.snapshot_type}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # Calculate state hash
    state_hash = hashlib.sha256(json.dumps(request.state_data, sort_keys=True).encode()).hexdigest()
    
    # Generate PQC signature
    snapshot_data = {
        "snapshot_id": snapshot_id,
        "proposal_id": proposal_id,
        "snapshot_type": request.snapshot_type,
        "state_hash": state_hash,
        "metadata": request.metadata,
        "created_at": datetime.utcnow().isoformat()
    }
    
    pqc_signature = generate_pqc_signature(snapshot_data)
    
    # Store snapshot
    snapshot_record = {
        **snapshot_data,
        "state_data": request.state_data,  # Store full data for rollback
        "pqc_signature": pqc_signature
    }
    
    state_snapshots[snapshot_id] = snapshot_record
    
    # Create audit entry
    audit_entry = {
        "audit_id": f"audit-{len(audit_trail.get(proposal_id, []))}",
        "proposal_id": proposal_id,
        "action": f"snapshot_{request.snapshot_type}",
        "actor": "decision-auditor",
        "details": {
            "snapshot_id": snapshot_id,
            "snapshot_type": request.snapshot_type,
            "state_hash": state_hash
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    audit_entry["audit_hash"] = calculate_audit_hash(audit_entry)
    
    # Store audit entry
    if proposal_id not in audit_trail:
        audit_trail[proposal_id] = []
    audit_trail[proposal_id].append(audit_entry)
    
    logger.info(f"Stored {request.snapshot_type} snapshot {snapshot_id} for proposal {proposal_id}")
    
    return {
        "snapshot_id": snapshot_id,
        "state_hash": state_hash,
        "pqc_signature": pqc_signature,
        "created_at": snapshot_data["created_at"]
    }

@app.post("/rollback/plan")
async def create_rollback_plan(request: RollbackRequest):
    """Create rollback plan (dry-run only in simulation)"""
    proposal_id = request.proposal_id
    target_snapshot_id = request.target_snapshot_id
    
    # Verify target snapshot exists
    if target_snapshot_id not in state_snapshots:
        raise HTTPException(status_code=404, detail="Target snapshot not found")
    
    target_snapshot = state_snapshots[target_snapshot_id]
    
    # Generate rollback plan ID
    rollback_id = f"rollback-{proposal_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # Create rollback steps (simulated)
    if not request.steps:
        rollback_steps = [
            {
                "step": 1,
                "action": "validate_current_state",
                "description": "Validate current system state before rollback"
            },
            {
                "step": 2,
                "action": "backup_current_state",
                "description": "Create backup of current state"
            },
            {
                "step": 3,
                "action": "restore_target_state",
                "description": f"Restore to snapshot {target_snapshot_id}",
                "target_hash": target_snapshot["state_hash"]
            },
            {
                "step": 4,
                "action": "verify_rollback",
                "description": "Verify rollback completed successfully"
            }
        ]
    else:
        rollback_steps = request.steps
    
    # Estimate duration and risk
    estimated_duration = f"{len(rollback_steps) * 2}-{len(rollback_steps) * 5} minutes"
    risk_level = "medium" if request.dry_run else "high"
    
    # Create rollback plan
    rollback_plan = {
        "rollback_id": rollback_id,
        "proposal_id": proposal_id,
        "target_snapshot": target_snapshot_id,
        "target_state_hash": target_snapshot["state_hash"],
        "dry_run": request.dry_run,
        "steps": rollback_steps,
        "estimated_duration": estimated_duration,
        "risk_level": risk_level,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Store rollback plan
    rollback_plans[rollback_id] = rollback_plan
    
    # Create audit entry
    audit_entry = {
        "audit_id": f"audit-rollback-{len(audit_trail.get(proposal_id, []))}",
        "proposal_id": proposal_id,
        "action": "rollback_plan_created",
        "actor": "decision-auditor",
        "details": {
            "rollback_id": rollback_id,
            "target_snapshot": target_snapshot_id,
            "dry_run": request.dry_run,
            "steps_count": len(rollback_steps)
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    audit_entry["audit_hash"] = calculate_audit_hash(audit_entry)
    
    if proposal_id not in audit_trail:
        audit_trail[proposal_id] = []
    audit_trail[proposal_id].append(audit_entry)
    
    logger.info(f"Created rollback plan {rollback_id} for proposal {proposal_id}")
    
    return {
        "rollback_id": rollback_id,
        "rollback_plan": rollback_plan,
        "simulation_mode": SIMULATION_MODE,
        "dry_run_only": request.dry_run or SIMULATION_MODE
    }

@app.get("/rollback/{rollback_id}")
async def get_rollback_plan(rollback_id: str):
    """Get rollback plan details"""
    if rollback_id not in rollback_plans:
        raise HTTPException(status_code=404, detail="Rollback plan not found")
    
    return rollback_plans[rollback_id]

@app.get("/snapshots/{proposal_id}")
async def list_snapshots(proposal_id: str):
    """List all snapshots for a proposal"""
    proposal_snapshots = [
        {
            "snapshot_id": snap_id,
            "snapshot_type": snap["snapshot_type"],
            "state_hash": snap["state_hash"],
            "created_at": snap["created_at"]
        }
        for snap_id, snap in state_snapshots.items()
        if snap["proposal_id"] == proposal_id
    ]
    
    return {
        "proposal_id": proposal_id,
        "snapshots": proposal_snapshots,
        "total_snapshots": len(proposal_snapshots)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint (P4)"""
    return {
        "status": "healthy",
        "service": "decision-auditor",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "audit_entries": sum(len(entries) for entries in audit_trail.values()),
        "snapshots_stored": len(state_snapshots),
        "rollback_plans": len(rollback_plans)
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint (P4)"""
    return JSONResponse(
        content=generate_latest().decode('utf-8'),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9206)