#!/usr/bin/env python3
"""
J.1.6 Ops API Gateway - Production operations API aggregation
"""

from fastapi import FastAPI, Request, HTTPException
import os, json, time, requests, logging

app = FastAPI(title="Ops API Gateway", version="1.0.0")
logger = logging.getLogger("ops-gateway")
logging.basicConfig(level=logging.INFO)

simulation_mode = os.getenv("SIMULATION_MODE", "true").lower() == "true"

# Service registry
services = {
    "deployment-orchestrator": {"url": "http://localhost:10001", "status": "unknown"},
    "canary-controller": {"url": "http://localhost:10002", "status": "unknown"},
    "telemetry-hub": {"url": "http://localhost:10003", "status": "unknown"},
    "billing-agent": {"url": "http://localhost:10004", "status": "unknown"},
    "launch-control-ui": {"url": "http://localhost:10005", "status": "unknown"}
}

@app.get("/health")
async def health():
    # Check all service health
    healthy_services = 0
    for service_name, service_info in services.items():
        try:
            if simulation_mode:
                service_info["status"] = "healthy"
                healthy_services += 1
            else:
                response = requests.get(f"{service_info['url']}/health", timeout=2)
                service_info["status"] = "healthy" if response.ok else "unhealthy"
                if response.ok:
                    healthy_services += 1
        except Exception:
            service_info["status"] = "unreachable"
    
    return {
        "status": "healthy" if healthy_services > 0 else "degraded",
        "service": "ops-gateway",
        "simulation_mode": simulation_mode,
        "services": services,
        "healthy_services": f"{healthy_services}/{len(services)}"
    }

@app.get("/metrics")
async def metrics():
    return {
        "gateway_requests_total": 0,  # Would track in production
        "services_registered": len(services),
        "services_healthy": sum(1 for s in services.values() if s["status"] == "healthy")
    }

@app.get("/v1/status")
async def get_system_status():
    """Get overall system status"""
    if simulation_mode:
        return {
            "system_status": "operational",
            "services": {
                name: {"status": "healthy", "uptime": "99.9%"}
                for name in services.keys()
            },
            "deployment_status": {
                "active_deployments": 3,
                "successful_deployments": 47,
                "failed_deployments": 2
            },
            "canary_status": {
                "active_canaries": 2,
                "successful_promotions": 23,
                "rollbacks": 1
            },
            "simulation_mode": True
        }
    else:
        # In production, would aggregate from all services
        return {"note": "Production status aggregation not implemented"}

@app.post("/v1/deploy")
async def deploy_service(request: Request):
    """Proxy deployment request to orchestrator"""
    body = await request.json()
    
    try:
        if simulation_mode:
            return {
                "deployment_id": f"sim_deploy_{int(time.time())}",
                "status": "started",
                "service_name": body.get("service_name", "unknown"),
                "simulation_mode": True
            }
        else:
            response = requests.post(
                f"{services['deployment-orchestrator']['url']}/v1/deploy",
                json=body,
                timeout=10
            )
            return response.json() if response.ok else {"error": "Deployment failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/canary/start")
async def start_canary(request: Request):
    """Proxy canary start request to controller"""
    body = await request.json()
    
    try:
        if simulation_mode:
            return {
                "canary_id": f"sim_canary_{int(time.time())}",
                "status": "started",
                "service_name": body.get("service_name", "unknown"),
                "traffic_percentage": body.get("traffic_percentage", 10),
                "simulation_mode": True
            }
        else:
            response = requests.post(
                f"{services['canary-controller']['url']}/v1/canary/start",
                json=body,
                timeout=10
            )
            return response.json() if response.ok else {"error": "Canary start failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/metrics/aggregate")
async def get_aggregate_metrics():
    """Get aggregated metrics from all services"""
    if simulation_mode:
        return {
            "deployments": {
                "total": 52,
                "successful": 47,
                "failed": 2,
                "active": 3
            },
            "canaries": {
                "total": 26,
                "promoted": 23,
                "rolled_back": 1,
                "active": 2
            },
            "system_health": {
                "availability": 99.9,
                "latency_p95": 145,
                "error_rate": 0.01
            },
            "costs": {
                "total_today": 127.45,
                "total_month": 2548.90,
                "budget_used_percent": 85
            },
            "simulation_mode": True
        }
    else:
        # In production, would collect from all services
        return {"note": "Production metrics aggregation not implemented"}

@app.post("/v1/emergency/stop")
async def emergency_stop():
    """Emergency stop all operations"""
    logger.critical("Emergency stop initiated")
    
    if simulation_mode:
        return {
            "status": "emergency_stop_simulated",
            "stopped_services": list(services.keys()),
            "timestamp": time.time(),
            "simulation_mode": True
        }
    else:
        # In production, would stop all deployments and canaries
        return {"note": "Production emergency stop not implemented"}

@app.get("/v1/audit/trail")
async def get_audit_trail():
    """Get audit trail for operations"""
    if simulation_mode:
        return {
            "audit_entries": [
                {
                    "timestamp": time.time() - 3600,
                    "action": "deployment_started",
                    "service": "aol-controller",
                    "user": "system",
                    "result": "success"
                },
                {
                    "timestamp": time.time() - 1800,
                    "action": "canary_promoted",
                    "service": "policy-engine", 
                    "user": "admin@atom.cloud",
                    "result": "success"
                },
                {
                    "timestamp": time.time() - 900,
                    "action": "budget_alert",
                    "service": "billing-agent",
                    "user": "system",
                    "result": "alert_sent"
                }
            ],
            "total_entries": 3,
            "simulation_mode": True
        }
    else:
        return {"note": "Production audit trail not implemented"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10006)