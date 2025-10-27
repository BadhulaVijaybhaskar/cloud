from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI(title="ATOM Backup API", version="1.0.0")

class BackupRequest(BaseModel):
    database: str
    description: str = ""

@app.get("/health")
def health():
    return {"status": "healthy", "service": "backup-api"}

@app.post("/create")
def create_backup(request: BackupRequest):
    """Create database backup"""
    backup_id = f"backup_{int(datetime.now().timestamp())}"
    
    if os.getenv("SIMULATION_MODE", "true").lower() == "true":
        return {
            "backup_id": backup_id,
            "status": "completed",
            "size_mb": 25.6,
            "created_at": datetime.now().isoformat()
        }
    
    # Real backup logic would go here
    return {"backup_id": backup_id, "status": "in_progress"}

@app.get("/list")
def list_backups():
    """List available backups"""
    if os.getenv("SIMULATION_MODE", "true").lower() == "true":
        return {
            "backups": [
                {"id": "backup_1703123456", "database": "main", "size_mb": 25.6, "created_at": "2024-01-01T10:00:00"},
                {"id": "backup_1703209856", "database": "main", "size_mb": 28.1, "created_at": "2024-01-02T10:00:00"}
            ]
        }
    
    return {"backups": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)