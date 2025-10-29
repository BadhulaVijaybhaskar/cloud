from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

app = FastAPI(title="ATOM Replication Controller", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class ReplicationJob(BaseModel):
    tenant_id: str
    source: str
    dest: str
    tables: List[str]
    options: Dict = {}

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: float = 0.0

# In-memory job store for simulation
jobs_db = {}

def enforce_p1_policy(tenant_id: str, tables: List[str]):
    """P1: Data Privacy - check for PII tables"""
    pii_tables = ["users", "profiles", "personal_data"]
    has_pii = any(table in pii_tables for table in tables)
    
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": "replication_check",
        "tenant_hash": hashlib.sha256(tenant_id.encode()).hexdigest()[:16],
        "has_pii": has_pii,
        "policy": "P1"
    }
    print(f"AUDIT: {json.dumps(audit_entry)}")
    return has_pii

def enforce_p2_policy(operation: str, tenant_id: str):
    """P2: Secrets & Signing - audit replication operations"""
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "tenant_hash": hashlib.sha256(tenant_id.encode()).hexdigest()[:16],
        "service": "replication-controller",
        "policy": "P2"
    }
    print(f"AUDIT: {json.dumps(audit_entry)}")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "replication-controller", "simulation": SIMULATION_MODE}

@app.post("/replication/jobs")
def create_replication_job(job: ReplicationJob):
    """Create cross-cloud replication job with P1/P2 enforcement"""
    
    # P1 Policy: Check for PII data
    has_pii = enforce_p1_policy(job.tenant_id, job.tables)
    if has_pii and not SIMULATION_MODE:
        # Real implementation would check for pii:replicate scope
        pass
    
    # P2 Policy: Audit operation
    enforce_p2_policy("create_job", job.tenant_id)
    
    job_id = hashlib.sha256(f"{job.tenant_id}{job.source}{job.dest}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
    
    if SIMULATION_MODE:
        jobs_db[job_id] = {
            "job_id": job_id,
            "tenant_id": job.tenant_id,
            "source": job.source,
            "dest": job.dest,
            "tables": job.tables,
            "status": "running",
            "progress": 0.0,
            "created_at": datetime.now().isoformat()
        }
        
        return {"job_id": job_id, "status": "created", "message": "Replication job started (simulation)"}
    
    raise HTTPException(status_code=503, detail="Replication infrastructure unavailable")

@app.get("/replication/jobs/{job_id}")
def get_job_status(job_id: str):
    """Get replication job status"""
    if SIMULATION_MODE:
        if job_id in jobs_db:
            job = jobs_db[job_id]
            # Simulate progress
            job["progress"] = min(100.0, job["progress"] + 25.0)
            if job["progress"] >= 100.0:
                job["status"] = "completed"
            return job
        raise HTTPException(status_code=404, detail="Job not found")
    
    raise HTTPException(status_code=503, detail="Job tracking unavailable")

@app.get("/replication/jobs")
def list_jobs(tenant_id: Optional[str] = None):
    """List replication jobs"""
    if SIMULATION_MODE:
        jobs = list(jobs_db.values())
        if tenant_id:
            jobs = [j for j in jobs if j["tenant_id"] == tenant_id]
        return {"jobs": jobs, "total": len(jobs)}
    
    raise HTTPException(status_code=503, detail="Job listing unavailable")

@app.get("/metrics")
def metrics():
    return {
        "jobs_total": len(jobs_db),
        "jobs_running": len([j for j in jobs_db.values() if j["status"] == "running"]),
        "simulation_mode": SIMULATION_MODE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8501)