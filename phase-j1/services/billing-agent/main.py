#!/usr/bin/env python3
"""
J.1.4 Billing Agent - Production cost tracking and governance
"""

from fastapi import FastAPI, Request
import os, json, time, random, logging
from typing import Dict, List

app = FastAPI(title="Billing Agent", version="1.0.0")
logger = logging.getLogger("billing-agent")
logging.basicConfig(level=logging.INFO)

# Global state
usage_records = {}
cost_alerts = []
budgets = {}
simulation_mode = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "billing-agent",
        "simulation_mode": simulation_mode,
        "tracked_services": len(usage_records),
        "active_budgets": len(budgets)
    }

@app.get("/metrics")
async def metrics():
    """P20: Cost telemetry metrics"""
    total_cost = sum(sum(r["cost"] for r in records) for records in usage_records.values())
    
    return {
        "billing_total_cost_usd": round(total_cost, 2),
        "billing_services_tracked": len(usage_records),
        "billing_alerts_active": len([a for a in cost_alerts if a["status"] == "active"]),
        "billing_budgets_exceeded": len([b for b in budgets.values() if b.get("exceeded", False)])
    }

@app.post("/v1/usage")
async def record_usage(request: Request):
    """Record resource usage for billing"""
    body = await request.json()
    
    service_name = body.get("service", "unknown")
    resource_type = body.get("resource_type", "compute")
    usage_amount = body.get("usage_amount", 0)
    unit_cost = body.get("unit_cost", 0.01)
    
    if service_name not in usage_records:
        usage_records[service_name] = []
    
    usage_record = {
        "timestamp": time.time(),
        "resource_type": resource_type,
        "usage_amount": usage_amount,
        "unit_cost": unit_cost,
        "cost": usage_amount * unit_cost,
        "region": body.get("region", "us-central1"),
        "tenant": body.get("tenant", "default")
    }
    
    usage_records[service_name].append(usage_record)
    
    # Check budget alerts
    check_budget_alerts(service_name, usage_record["cost"])
    
    logger.info(f"Recorded usage for {service_name}: ${usage_record['cost']:.4f}")
    
    return {
        "status": "recorded",
        "service": service_name,
        "cost": usage_record["cost"]
    }

@app.post("/v1/budgets")
async def create_budget(request: Request):
    """Create cost budget for service or tenant"""
    body = await request.json()
    
    budget_id = body.get("budget_id", f"budget_{int(time.time())}")
    
    budget = {
        "id": budget_id,
        "name": body.get("name", "Unnamed Budget"),
        "limit_usd": body.get("limit_usd", 100.0),
        "period": body.get("period", "monthly"),
        "scope": body.get("scope", "service"),
        "target": body.get("target", "all"),
        "alert_threshold": body.get("alert_threshold", 0.8),
        "created_at": time.time(),
        "exceeded": False
    }
    
    budgets[budget_id] = budget
    
    logger.info(f"Created budget {budget_id}: ${budget['limit_usd']}")
    
    return budget

@app.get("/v1/costs/{service_name}")
async def get_service_costs(service_name: str):
    """Get cost breakdown for service"""
    if service_name not in usage_records:
        return {"service": service_name, "total_cost": 0, "records": []}
    
    records = usage_records[service_name]
    total_cost = sum(r["cost"] for r in records)
    
    # Group by resource type
    cost_by_resource = {}
    for record in records:
        resource_type = record["resource_type"]
        if resource_type not in cost_by_resource:
            cost_by_resource[resource_type] = 0
        cost_by_resource[resource_type] += record["cost"]
    
    return {
        "service": service_name,
        "total_cost": round(total_cost, 4),
        "cost_by_resource": cost_by_resource,
        "record_count": len(records)
    }

@app.get("/v1/dashboard")
async def get_billing_dashboard():
    """Get billing dashboard data"""
    if simulation_mode:
        # Generate synthetic billing data
        services = ["aol-controller", "neural-fabric", "global-router", "policy-engine"]
        dashboard_data = {
            "total_cost_today": round(random.uniform(50, 200), 2),
            "total_cost_month": round(random.uniform(1000, 5000), 2),
            "cost_by_service": {
                service: round(random.uniform(10, 100), 2) 
                for service in services
            },
            "cost_trend": [
                {"date": f"2024-12-{i:02d}", "cost": round(random.uniform(40, 80), 2)}
                for i in range(1, 20)
            ],
            "budget_status": {
                "monthly_limit": 3000.0,
                "current_spend": round(random.uniform(1500, 2500), 2),
                "projected_spend": round(random.uniform(2800, 3200), 2)
            },
            "top_cost_drivers": [
                {"resource": "compute", "cost": round(random.uniform(500, 1000), 2)},
                {"resource": "storage", "cost": round(random.uniform(200, 400), 2)},
                {"resource": "network", "cost": round(random.uniform(100, 300), 2)}
            ],
            "simulation_mode": True
        }
        return dashboard_data
    else:
        return {"note": "Production billing dashboard not implemented"}

def check_budget_alerts(service_name: str, cost: float):
    """Check if any budgets are exceeded"""
    for budget_id, budget in budgets.items():
        if budget["scope"] == "service" and budget["target"] == service_name:
            # Calculate current spend for this budget period
            current_spend = sum(r["cost"] for r in usage_records.get(service_name, []))
            
            if current_spend >= budget["limit_usd"] * budget["alert_threshold"]:
                alert = {
                    "id": f"alert_{int(time.time())}",
                    "budget_id": budget_id,
                    "service": service_name,
                    "current_spend": current_spend,
                    "budget_limit": budget["limit_usd"],
                    "threshold": budget["alert_threshold"],
                    "status": "active",
                    "created_at": time.time()
                }
                
                cost_alerts.append(alert)
                budget["exceeded"] = current_spend >= budget["limit_usd"]
                
                logger.warning(f"Budget alert: {service_name} spend ${current_spend:.2f} exceeds threshold")

@app.get("/v1/alerts")
async def get_cost_alerts():
    """Get active cost alerts"""
    return {
        "alerts": [a for a in cost_alerts if a["status"] == "active"],
        "total": len(cost_alerts)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10004)