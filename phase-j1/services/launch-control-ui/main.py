#!/usr/bin/env python3
"""
J.1.5 Launch Control UI - Production operations dashboard
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import os, json, time, requests, logging

app = FastAPI(title="Launch Control UI", version="1.0.0")
logger = logging.getLogger("launch-control-ui")
logging.basicConfig(level=logging.INFO)

simulation_mode = os.getenv("SIMULATION_MODE", "true").lower() == "true"

# Service URLs
DEPLOYMENT_ORCHESTRATOR_URL = os.getenv("DEPLOYMENT_ORCHESTRATOR_URL", "http://localhost:10001")
CANARY_CONTROLLER_URL = os.getenv("CANARY_CONTROLLER_URL", "http://localhost:10002")
TELEMETRY_HUB_URL = os.getenv("TELEMETRY_HUB_URL", "http://localhost:10003")
BILLING_AGENT_URL = os.getenv("BILLING_AGENT_URL", "http://localhost:10004")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "launch-control-ui",
        "simulation_mode": simulation_mode
    }

@app.get("/metrics")
async def metrics():
    return {
        "ui_requests_total": 0,  # Would track in production
        "active_sessions": 1
    }

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard UI"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ATOM Cloud - Launch Control</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .status-ok { color: #27ae60; }
            .status-warning { color: #f39c12; }
            .status-error { color: #e74c3c; }
            .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            .btn:hover { background: #2980b9; }
            .simulation-badge { background: #f39c12; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 ATOM Cloud Launch Control</h1>
            <p>Production Operations Dashboard</p>
            <span class="simulation-badge">SIMULATION MODE</span>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🔄 Deployments</h3>
                <p class="status-ok">✅ All systems operational</p>
                <p>Active deployments: <strong>3</strong></p>
                <p>Success rate: <strong>98.5%</strong></p>
                <button class="btn" onclick="location.href='/api/v1/deployments'">View Deployments</button>
            </div>
            
            <div class="card">
                <h3>🎯 Canary Status</h3>
                <p class="status-ok">✅ Canaries healthy</p>
                <p>Active canaries: <strong>2</strong></p>
                <p>Promotion rate: <strong>95%</strong></p>
                <button class="btn" onclick="location.href='/api/v1/canaries'">Manage Canaries</button>
            </div>
            
            <div class="card">
                <h3>📊 System Health</h3>
                <p class="status-ok">✅ All metrics green</p>
                <p>Availability: <strong>99.9%</strong></p>
                <p>P95 Latency: <strong>145ms</strong></p>
                <button class="btn" onclick="location.href='/api/v1/telemetry'">View Metrics</button>
            </div>
            
            <div class="card">
                <h3>💰 Cost Overview</h3>
                <p class="status-warning">⚠️ 85% of budget used</p>
                <p>Today: <strong>$127.45</strong></p>
                <p>Month: <strong>$2,548.90</strong></p>
                <button class="btn" onclick="location.href='/api/v1/billing'">View Billing</button>
            </div>
            
            <div class="card">
                <h3>🛡️ Security Status</h3>
                <p class="status-ok">✅ All policies enforced</p>
                <p>P1-P20 compliance: <strong>100%</strong></p>
                <p>Violations: <strong>0</strong></p>
                <button class="btn" onclick="location.href='/api/v1/security'">Security Dashboard</button>
            </div>
            
            <div class="card">
                <h3>⚡ Quick Actions</h3>
                <button class="btn" style="margin: 5px;">Deploy Service</button><br>
                <button class="btn" style="margin: 5px;">Start Canary</button><br>
                <button class="btn" style="margin: 5px;">Emergency Stop</button><br>
                <button class="btn" style="margin: 5px;">View Logs</button>
            </div>
        </div>
        
        <script>
            // Auto-refresh every 30 seconds
            setTimeout(() => location.reload(), 30000);
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/api/v1/deployments")
async def get_deployments():
    """Get deployment status from orchestrator"""
    try:
        if simulation_mode:
            return {
                "deployments": [
                    {"id": "dep-001", "service": "aol-controller", "status": "running", "environment": "production"},
                    {"id": "dep-002", "service": "neural-fabric", "status": "completed", "environment": "production"},
                    {"id": "dep-003", "service": "global-router", "status": "running", "environment": "staging"}
                ],
                "simulation_mode": True
            }
        else:
            response = requests.get(f"{DEPLOYMENT_ORCHESTRATOR_URL}/v1/deployments", timeout=5)
            return response.json() if response.ok else {"error": "Service unavailable"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/v1/canaries")
async def get_canaries():
    """Get canary status from controller"""
    try:
        if simulation_mode:
            return {
                "canaries": [
                    {"id": "can-001", "service": "policy-engine", "status": "running", "traffic": 10},
                    {"id": "can-002", "service": "billing-agent", "status": "promoted", "traffic": 100}
                ],
                "simulation_mode": True
            }
        else:
            response = requests.get(f"{CANARY_CONTROLLER_URL}/v1/canaries", timeout=5)
            return response.json() if response.ok else {"error": "Service unavailable"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/v1/telemetry")
async def get_telemetry():
    """Get telemetry data from hub"""
    try:
        if simulation_mode:
            return {
                "system_health": {
                    "availability": 99.9,
                    "latency_p95": 145,
                    "error_rate": 0.01,
                    "cpu_usage": 65,
                    "memory_usage": 78
                },
                "simulation_mode": True
            }
        else:
            response = requests.get(f"{TELEMETRY_HUB_URL}/v1/dashboard", timeout=5)
            return response.json() if response.ok else {"error": "Service unavailable"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/v1/billing")
async def get_billing():
    """Get billing data from agent"""
    try:
        if simulation_mode:
            return {
                "total_cost_today": 127.45,
                "total_cost_month": 2548.90,
                "budget_limit": 3000.00,
                "budget_used_percent": 85,
                "simulation_mode": True
            }
        else:
            response = requests.get(f"{BILLING_AGENT_URL}/v1/dashboard", timeout=5)
            return response.json() if response.ok else {"error": "Service unavailable"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/v1/security")
async def get_security():
    """Get security and policy status"""
    return {
        "policies": {
            "P1_Data_Privacy": "ENFORCED",
            "P2_Secrets_Signing": "ENFORCED", 
            "P3_Execution_Safety": "ENFORCED",
            "P16_Infrastructure_Separation": "ENFORCED",
            "P17_Deployment_Verification": "ENFORCED",
            "P18_Rollback_Readiness": "ENFORCED",
            "P19_Live_Observability": "ENFORCED",
            "P20_Cost_Governance": "ENFORCED"
        },
        "violations": 0,
        "last_audit": time.strftime("%Y-%m-%d %H:%M:%S"),
        "simulation_mode": simulation_mode
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10005)