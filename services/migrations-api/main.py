from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os

app = FastAPI(title="ATOM Migrations API", version="1.0.0")

class Migration(BaseModel):
    name: str
    sql: str
    description: str = ""

@app.get("/health")
def health():
    return {"status": "healthy", "service": "migrations-api"}

@app.get("/list")
def list_migrations():
    """List available migrations"""
    if os.getenv("SIMULATION_MODE", "true").lower() == "true":
        return {
            "migrations": [
                {"id": "001_initial_schema", "status": "applied", "applied_at": "2024-01-01T10:00:00"},
                {"id": "002_add_indexes", "status": "applied", "applied_at": "2024-01-01T11:00:00"},
                {"id": "003_user_roles", "status": "pending", "applied_at": None}
            ]
        }
    
    return {"migrations": []}

@app.post("/apply")
def apply_migration(migration: Migration):
    """Apply database migration"""
    if os.getenv("SIMULATION_MODE", "true").lower() == "true":
        return {
            "migration_id": migration.name,
            "status": "applied",
            "message": "Migration applied successfully (simulation)"
        }
    
    # Real migration logic would go here
    return {"status": "pending"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)