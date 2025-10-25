#!/usr/bin/env python3
"""
Marketplace Registry Service - E.1
Handles WPK publishing, review, and marketplace operations
"""
import os
import json
import time
import uuid
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

app = FastAPI(title="Marketplace Registry", version="1.0.0")
security = HTTPBearer()

# Environment
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
DB_PATH = os.getenv("MARKETPLACE_DB", "/tmp/marketplace.db")

class WPKUpload(BaseModel):
    name: str
    version: str
    content: dict
    signature: str

class WPKReview(BaseModel):
    status: str  # "approved" or "rejected"
    reason: Optional[str] = None

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS wpks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT NOT NULL,
            content TEXT NOT NULL,
            signature TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at INTEGER NOT NULL,
            reviewed_at INTEGER,
            review_reason TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup():
    init_db()
    print(f"Marketplace Registry started (SIMULATION_MODE={SIMULATION_MODE})")

@app.post("/wpk/upload")
async def upload_wpk(wpk: WPKUpload, token: str = Depends(security)):
    wpk_id = str(uuid.uuid4())
    
    # Simulate signature verification
    if SIMULATION_MODE:
        sig_valid = len(wpk.signature) > 10
    else:
        # TODO: Real cosign verification
        sig_valid = True
    
    if not sig_valid:
        raise HTTPException(400, "Invalid signature")
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO wpks (id, name, version, content, signature, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (wpk_id, wpk.name, wpk.version, json.dumps(wpk.content), wpk.signature, int(time.time())))
    conn.commit()
    conn.close()
    
    return {"id": wpk_id, "status": "uploaded", "message": "WPK uploaded for review"}

@app.get("/wpk/list")
async def list_wpks(status: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    if status:
        cursor = conn.execute("SELECT id, name, version, status, created_at FROM wpks WHERE status = ?", (status,))
    else:
        cursor = conn.execute("SELECT id, name, version, status, created_at FROM wpks")
    
    wpks = []
    for row in cursor.fetchall():
        wpks.append({
            "id": row[0],
            "name": row[1], 
            "version": row[2],
            "status": row[3],
            "created_at": row[4]
        })
    conn.close()
    
    return {"wpks": wpks, "count": len(wpks)}

@app.post("/wpk/review/{wpk_id}")
async def review_wpk(wpk_id: str, review: WPKReview, token: str = Depends(security)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT id FROM wpks WHERE id = ?", (wpk_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(404, "WPK not found")
    
    conn.execute("""
        UPDATE wpks SET status = ?, reviewed_at = ?, review_reason = ?
        WHERE id = ?
    """, (review.status, int(time.time()), review.reason, wpk_id))
    conn.commit()
    conn.close()
    
    return {"id": wpk_id, "status": review.status, "message": f"WPK {review.status}"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "marketplace-registry", "simulation_mode": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT status, COUNT(*) FROM wpks GROUP BY status")
    metrics = {}
    for row in cursor.fetchall():
        metrics[f"wpks_{row[0]}"] = row[1]
    conn.close()
    
    return {"marketplace_wpks_total": sum(metrics.values()), **metrics}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050)