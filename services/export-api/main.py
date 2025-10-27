from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os

app = FastAPI(title="ATOM Export API", version="1.0.0")

class ExportRequest(BaseModel):
    table: str
    format: str = "csv"
    filters: Dict[str, Any] = {}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "export-api"}

@app.post("/export")
def export_data(request: ExportRequest):
    """Export table data"""
    if os.getenv("SIMULATION_MODE", "true").lower() == "true":
        return {
            "export_id": f"export_{request.table}_{request.format}",
            "download_url": f"/downloads/export_{request.table}.{request.format}",
            "status": "ready",
            "rows_exported": 150
        }
    
    # Real export logic would go here
    return {"status": "processing"}

@app.get("/webhooks")
def list_webhooks():
    """List configured webhooks"""
    if os.getenv("SIMULATION_MODE", "true").lower() == "true":
        return {
            "webhooks": [
                {"id": "wh_001", "url": "https://api.example.com/webhook", "events": ["insert", "update"]},
                {"id": "wh_002", "url": "https://slack.com/webhook/123", "events": ["delete"]}
            ]
        }
    
    return {"webhooks": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)