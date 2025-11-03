#!/usr/bin/env python3
"""
ATOM Payment Engine - J.3.3
Stripe integration, revenue sharing, analytics
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import hashlib
import time
from datetime import datetime, timedelta
from typing import List

app = FastAPI(title="ATOM Payment Engine", version="1.0.0")

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

class Purchase(BaseModel):
    package_id: str
    user_id: str
    amount: int  # cents
    payment_method: str = "card"

class Payout(BaseModel):
    vendor_id: str
    amount: int
    currency: str = "USD"

# Simulation data
transactions_db = {}
revenue_db = {}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "payment-engine",
        "simulation_mode": SIMULATION_MODE,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/billing/purchase")
async def process_purchase(purchase: Purchase):
    """Process package purchase"""
    
    transaction_id = hashlib.sha256(f"{purchase.package_id}{purchase.user_id}{time.time()}".encode()).hexdigest()[:16]
    
    # Simulate payment processing
    if not SIMULATION_MODE:
        # In production: integrate with Stripe
        # stripe.PaymentIntent.create(amount=purchase.amount, currency='usd')
        pass
    
    # Calculate revenue split (70% vendor, 30% platform)
    vendor_amount = int(purchase.amount * 0.70)
    platform_amount = purchase.amount - vendor_amount
    
    transaction = {
        "id": transaction_id,
        "package_id": purchase.package_id,
        "user_id": purchase.user_id,
        "amount": purchase.amount,
        "vendor_amount": vendor_amount,
        "platform_amount": platform_amount,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "payment_method": purchase.payment_method
    }
    
    transactions_db[transaction_id] = transaction
    
    # Update revenue tracking
    vendor_id = f"vendor-{hash(purchase.package_id) % 100}"
    if vendor_id not in revenue_db:
        revenue_db[vendor_id] = {"total": 0, "transactions": []}
    
    revenue_db[vendor_id]["total"] += vendor_amount
    revenue_db[vendor_id]["transactions"].append(transaction_id)
    
    return {
        "transaction_id": transaction_id,
        "status": "completed",
        "amount": purchase.amount,
        "vendor_amount": vendor_amount,
        "platform_fee": platform_amount,
        "simulation_mode": SIMULATION_MODE
    }

@app.get("/billing/revenue/{vendor_id}")
async def get_revenue(vendor_id: str):
    """Get vendor revenue analytics"""
    
    if vendor_id not in revenue_db:
        return {
            "vendor_id": vendor_id,
            "total_revenue": 0,
            "transaction_count": 0,
            "last_30_days": 0,
            "simulation_mode": SIMULATION_MODE
        }
    
    vendor_data = revenue_db[vendor_id]
    
    # Calculate last 30 days revenue
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_revenue = 0
    
    for tx_id in vendor_data["transactions"]:
        if tx_id in transactions_db:
            tx = transactions_db[tx_id]
            tx_date = datetime.fromisoformat(tx["created_at"].replace('Z', '+00:00'))
            if tx_date >= thirty_days_ago:
                recent_revenue += tx["vendor_amount"]
    
    return {
        "vendor_id": vendor_id,
        "total_revenue": vendor_data["total"],
        "transaction_count": len(vendor_data["transactions"]),
        "last_30_days": recent_revenue,
        "average_transaction": vendor_data["total"] // max(1, len(vendor_data["transactions"])),
        "simulation_mode": SIMULATION_MODE
    }

@app.post("/billing/payout")
async def process_payout(payout: Payout):
    """Process vendor payout"""
    
    payout_id = hashlib.sha256(f"{payout.vendor_id}{payout.amount}{time.time()}".encode()).hexdigest()[:16]
    
    if not SIMULATION_MODE:
        # In production: integrate with Stripe Connect
        # stripe.Transfer.create(amount=payout.amount, destination=vendor_stripe_account)
        pass
    
    # Update vendor balance
    if payout.vendor_id in revenue_db:
        revenue_db[payout.vendor_id]["total"] -= payout.amount
    
    return {
        "payout_id": payout_id,
        "vendor_id": payout.vendor_id,
        "amount": payout.amount,
        "currency": payout.currency,
        "status": "completed",
        "processed_at": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE
    }

@app.get("/billing/transactions")
async def get_transactions(limit: int = 50):
    """Get recent transactions"""
    
    transactions = list(transactions_db.values())
    transactions.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "transactions": transactions[:limit],
        "total": len(transactions),
        "simulation_mode": SIMULATION_MODE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9303)