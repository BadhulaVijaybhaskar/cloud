#!/usr/bin/env python3
"""
Billing & Metering Service - E.3
Handles usage tracking and payment processing
"""
import os
import json
import time
import uuid
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Dict, List, Optional
import sqlite3
from datetime import datetime, timedelta

app = FastAPI(title="Billing & Metering", version="1.0.0")
security = HTTPBearer()

# Environment
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
DB_PATH = os.getenv("BILLING_DB", "/tmp/billing.db")
STRIPE_KEY = os.getenv("STRIPE_KEY", "sk_test_simulation")

class UsageReport(BaseModel):
    tenant_id: str
    service: str
    usage_type: str
    quantity: float
    timestamp: Optional[int] = None

class Invoice(BaseModel):
    tenant_id: str
    period_start: int
    period_end: int
    items: List[Dict]
    total_amount: float
    currency: str = "USD"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_records (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            service TEXT NOT NULL,
            usage_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            timestamp INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            period_start INTEGER NOT NULL,
            period_end INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            status TEXT DEFAULT 'pending',
            created_at INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup():
    init_db()
    print(f"Billing & Metering started (SIMULATION_MODE={SIMULATION_MODE})")

@app.post("/usage/report")
async def report_usage(usage: UsageReport, token: str = Depends(security)):
    """Submit usage metrics for billing"""
    usage_id = str(uuid.uuid4())
    timestamp = usage.timestamp or int(time.time())
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO usage_records (id, tenant_id, service, usage_type, quantity, timestamp, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (usage_id, usage.tenant_id, usage.service, usage.usage_type, usage.quantity, timestamp, int(time.time())))
    conn.commit()
    conn.close()
    
    return {
        "id": usage_id,
        "status": "recorded",
        "tenant_id": usage.tenant_id,
        "quantity": usage.quantity,
        "message": "Usage recorded successfully"
    }

@app.get("/billing/invoice/{tenant_id}")
async def get_invoice(tenant_id: str, period: Optional[str] = "current"):
    """Retrieve latest invoice for tenant"""
    
    # Calculate period
    now = datetime.now()
    if period == "current":
        period_start = int(now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp())
        period_end = int(now.timestamp())
    else:
        # Default to last 30 days
        period_end = int(now.timestamp())
        period_start = int((now - timedelta(days=30)).timestamp())
    
    # Get usage for period
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        SELECT service, usage_type, SUM(quantity) as total_quantity
        FROM usage_records 
        WHERE tenant_id = ? AND timestamp BETWEEN ? AND ?
        GROUP BY service, usage_type
    """, (tenant_id, period_start, period_end))
    
    usage_items = []
    total_amount = 0.0
    
    # Simulate pricing
    pricing = {
        "marketplace": {"wpk_upload": 0.10, "wpk_review": 0.05},
        "analytics": {"query": 0.01, "report": 0.25},
        "storage": {"gb_hour": 0.02},
        "compute": {"cpu_hour": 0.50, "memory_gb_hour": 0.10}
    }
    
    for row in cursor.fetchall():
        service, usage_type, quantity = row
        rate = pricing.get(service, {}).get(usage_type, 0.01)
        amount = quantity * rate
        total_amount += amount
        
        usage_items.append({
            "service": service,
            "usage_type": usage_type,
            "quantity": quantity,
            "rate": rate,
            "amount": round(amount, 2)
        })
    
    conn.close()
    
    # Generate invoice
    invoice = {
        "id": f"inv_{tenant_id}_{period_start}",
        "tenant_id": tenant_id,
        "period_start": period_start,
        "period_end": period_end,
        "items": usage_items,
        "total_amount": round(total_amount, 2),
        "currency": "USD",
        "status": "generated",
        "generated_at": int(time.time())
    }
    
    if SIMULATION_MODE:
        invoice["stripe_simulation"] = True
        invoice["payment_method"] = "sim_card_4242"
    
    return invoice

@app.get("/billing/usage/{tenant_id}")
async def get_usage_summary(tenant_id: str, days: int = 30):
    """Get usage summary for tenant"""
    
    cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        SELECT service, usage_type, SUM(quantity) as total, COUNT(*) as records
        FROM usage_records 
        WHERE tenant_id = ? AND timestamp >= ?
        GROUP BY service, usage_type
        ORDER BY service, usage_type
    """, (tenant_id, cutoff))
    
    usage_summary = []
    for row in cursor.fetchall():
        usage_summary.append({
            "service": row[0],
            "usage_type": row[1],
            "total_quantity": row[2],
            "record_count": row[3]
        })
    
    conn.close()
    
    return {
        "tenant_id": tenant_id,
        "period_days": days,
        "usage_summary": usage_summary,
        "total_services": len(set(item["service"] for item in usage_summary))
    }

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "service": "billing-metering",
        "simulation_mode": SIMULATION_MODE,
        "stripe_configured": bool(STRIPE_KEY and STRIPE_KEY != "sk_test_simulation")
    }

@app.get("/metrics")
async def metrics():
    conn = sqlite3.connect(DB_PATH)
    
    # Usage metrics
    cursor = conn.execute("SELECT COUNT(*) FROM usage_records")
    total_usage_records = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(DISTINCT tenant_id) FROM usage_records")
    active_tenants = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(*) FROM invoices")
    total_invoices = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "billing_usage_records_total": total_usage_records,
        "billing_active_tenants": active_tenants,
        "billing_invoices_total": total_invoices
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8060)