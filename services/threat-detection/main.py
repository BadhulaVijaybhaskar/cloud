from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import hashlib

app = FastAPI(title="ATOM Threat Detection", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class ThreatEvent(BaseModel):
    source_ip: str
    target: str
    event_type: str
    severity: str = "medium"
    payload: Dict[str, Any] = {}

class ThreatRule(BaseModel):
    name: str
    pattern: str
    action: str = "alert"
    threshold: int = 5

# In-memory threat storage for simulation
active_threats = []
blocked_ips = set()
threat_rules = [
    {"name": "Brute Force Detection", "pattern": "failed_login", "threshold": 5, "action": "block"},
    {"name": "SQL Injection", "pattern": "sql_injection", "threshold": 1, "action": "block"},
    {"name": "Rate Limiting", "pattern": "high_frequency", "threshold": 100, "action": "throttle"}
]

def log_threat(threat_data: Dict[str, Any]):
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "service": "threat-detection",
        "threat": threat_data,
        "sha256": hashlib.sha256(json.dumps(threat_data, sort_keys=True).encode()).hexdigest()
    }
    
    os.makedirs("reports/logs", exist_ok=True)
    with open("reports/logs/threat_detection.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "threat-detection",
        "env": "SIM" if SIMULATION_MODE else "LIVE",
        "active_threats": len(active_threats),
        "blocked_ips": len(blocked_ips),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/analyze")
async def analyze_threat(event: ThreatEvent, background_tasks: BackgroundTasks):
    threat_id = f"threat-{int(time.time())}-{hash(event.source_ip) % 10000}"
    
    # Simulate threat analysis
    risk_score = 0
    detected_patterns = []
    
    if SIMULATION_MODE:
        # Simulate various threat patterns
        if "admin" in event.payload.get("username", "").lower():
            risk_score += 30
            detected_patterns.append("admin_access_attempt")
        
        if event.event_type == "failed_login":
            risk_score += 20
            detected_patterns.append("authentication_failure")
        
        if "SELECT" in str(event.payload).upper() and ("UNION" in str(event.payload).upper() or "DROP" in str(event.payload).upper()):
            risk_score += 80
            detected_patterns.append("sql_injection")
            event.severity = "critical"
        
        if event.source_ip in ["192.168.1.100", "10.0.0.50"]:
            risk_score += 40
            detected_patterns.append("suspicious_ip")
    
    # Determine action based on risk score
    action_taken = "logged"
    if risk_score >= 70:
        action_taken = "blocked"
        blocked_ips.add(event.source_ip)
        event.severity = "high"
    elif risk_score >= 40:
        action_taken = "flagged"
        event.severity = "medium"
    
    threat_data = {
        "id": threat_id,
        "source_ip": event.source_ip,
        "target": event.target,
        "event_type": event.event_type,
        "severity": event.severity,
        "risk_score": risk_score,
        "detected_patterns": detected_patterns,
        "action_taken": action_taken,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": event.payload
    }
    
    active_threats.append(threat_data)
    
    # Keep only last 100 threats in memory
    if len(active_threats) > 100:
        active_threats.pop(0)
    
    # Log threat asynchronously
    background_tasks.add_task(log_threat, threat_data)
    
    return {
        "threat_id": threat_id,
        "risk_score": risk_score,
        "severity": event.severity,
        "action_taken": action_taken,
        "detected_patterns": detected_patterns,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/threats/active")
async def get_active_threats():
    # Filter threats from last 24 hours
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    
    recent_threats = []
    for threat in active_threats:
        threat_time = datetime.fromisoformat(threat["timestamp"].replace("Z", "+00:00"))
        if threat_time > cutoff_time:
            recent_threats.append(threat)
    
    return {
        "threats": recent_threats,
        "count": len(recent_threats),
        "blocked_ips": list(blocked_ips),
        "summary": {
            "critical": len([t for t in recent_threats if t["severity"] == "critical"]),
            "high": len([t for t in recent_threats if t["severity"] == "high"]),
            "medium": len([t for t in recent_threats if t["severity"] == "medium"]),
            "low": len([t for t in recent_threats if t["severity"] == "low"])
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/threats/{threat_id}")
async def get_threat_details(threat_id: str):
    threat = next((t for t in active_threats if t["id"] == threat_id), None)
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    
    return threat

@app.post("/threats/{threat_id}/resolve")
async def resolve_threat(threat_id: str):
    threat = next((t for t in active_threats if t["id"] == threat_id), None)
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    
    threat["status"] = "resolved"
    threat["resolved_at"] = datetime.utcnow().isoformat()
    
    # Remove from blocked IPs if it was blocked
    if threat["source_ip"] in blocked_ips:
        blocked_ips.remove(threat["source_ip"])
    
    return {
        "threat_id": threat_id,
        "status": "resolved",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/rules")
async def get_threat_rules():
    return {
        "rules": threat_rules,
        "count": len(threat_rules),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/rules")
async def create_threat_rule(rule: ThreatRule):
    rule_data = {
        "id": f"rule-{int(time.time())}",
        "name": rule.name,
        "pattern": rule.pattern,
        "action": rule.action,
        "threshold": rule.threshold,
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    }
    
    threat_rules.append(rule_data)
    
    return {
        "rule_id": rule_data["id"],
        "status": "created",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/blocked-ips")
async def get_blocked_ips():
    return {
        "blocked_ips": list(blocked_ips),
        "count": len(blocked_ips),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/blocked-ips/{ip}/unblock")
async def unblock_ip(ip: str):
    if ip in blocked_ips:
        blocked_ips.remove(ip)
        return {
            "ip": ip,
            "status": "unblocked",
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        raise HTTPException(status_code=404, detail="IP not found in blocked list")

@app.get("/metrics")
async def metrics():
    return f"""# HELP threats_detected_total Total number of threats detected
# TYPE threats_detected_total counter
threats_detected_total{{severity="critical"}} {len([t for t in active_threats if t["severity"] == "critical"])}
threats_detected_total{{severity="high"}} {len([t for t in active_threats if t["severity"] == "high"])}
threats_detected_total{{severity="medium"}} {len([t for t in active_threats if t["severity"] == "medium"])}
threats_detected_total{{severity="low"}} {len([t for t in active_threats if t["severity"] == "low"])}

# HELP blocked_ips_total Number of blocked IP addresses
# TYPE blocked_ips_total gauge
blocked_ips_total {len(blocked_ips)}

# HELP threat_rules_active Number of active threat detection rules
# TYPE threat_rules_active gauge
threat_rules_active {len(threat_rules)}
"""

# Background task to generate synthetic threats in simulation mode
async def generate_synthetic_threats():
    if not SIMULATION_MODE:
        return
    
    synthetic_events = [
        {"source_ip": "192.168.1.100", "target": "auth-api", "event_type": "failed_login", "payload": {"username": "admin"}},
        {"source_ip": "10.0.0.50", "target": "data-api", "event_type": "suspicious_query", "payload": {"query": "SELECT * FROM users UNION SELECT * FROM passwords"}},
        {"source_ip": "172.16.0.25", "target": "storage-api", "event_type": "unauthorized_access", "payload": {"path": "/admin/secrets"}},
    ]
    
    while True:
        await asyncio.sleep(30)  # Generate threat every 30 seconds
        import random
        event_data = random.choice(synthetic_events)
        
        event = ThreatEvent(
            source_ip=event_data["source_ip"],
            target=event_data["target"],
            event_type=event_data["event_type"],
            payload=event_data["payload"]
        )
        
        # Analyze the synthetic threat
        await analyze_threat(event, BackgroundTasks())

@app.on_event("startup")
async def startup_event():
    if SIMULATION_MODE:
        asyncio.create_task(generate_synthetic_threats())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)