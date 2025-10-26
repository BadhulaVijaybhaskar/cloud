from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import hashlib
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
import jwt

app = FastAPI(title="ATOM Security Fabric", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
SECRET_KEY = os.getenv("JWT_SECRET", "atom-security-fabric-key")

class SecurityScan(BaseModel):
    target: str
    scan_type: str = "vulnerability"
    depth: str = "standard"

class ThreatAlert(BaseModel):
    severity: str
    source: str
    description: str
    mitigation: Optional[str] = None

class PolicyRule(BaseModel):
    name: str
    condition: str
    action: str
    priority: int = 1

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"user": "anonymous", "tenant": "default"}
    
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        return {"user": "anonymous", "tenant": "default"}

def audit_log(action: str, user: str, tenant: str, details: Dict[str, Any]):
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "action": action,
        "user": user,
        "tenant": tenant,
        "details": details,
        "sha256": hashlib.sha256(json.dumps(details, sort_keys=True).encode()).hexdigest()
    }
    
    os.makedirs("reports/logs", exist_ok=True)
    with open("reports/logs/security_audit.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "security-fabric",
        "env": "SIM" if SIMULATION_MODE else "LIVE",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/scan/vulnerability")
async def vulnerability_scan(scan: SecurityScan, auth=Depends(verify_token)):
    audit_log("vulnerability_scan", auth.get("user", "anonymous"), auth.get("tenant", "default"), {
        "target": scan.target,
        "scan_type": scan.scan_type,
        "depth": scan.depth
    })
    
    if SIMULATION_MODE:
        return {
            "scan_id": f"vuln-{int(time.time())}",
            "status": "completed",
            "vulnerabilities": [
                {
                    "id": "CVE-SIM-001",
                    "severity": "medium",
                    "component": "example-lib",
                    "description": "Simulated vulnerability for testing",
                    "remediation": "Update to latest version"
                }
            ],
            "summary": {
                "critical": 0,
                "high": 0,
                "medium": 1,
                "low": 2,
                "info": 5
            },
            "mode": "simulation"
        }
    
    raise HTTPException(status_code=503, detail="Live vulnerability scanning not configured")

@app.post("/scan/compliance")
async def compliance_scan(scan: SecurityScan, auth=Depends(verify_token)):
    audit_log("compliance_scan", auth.get("user", "anonymous"), auth.get("tenant", "default"), {
        "target": scan.target,
        "scan_type": scan.scan_type
    })
    
    if SIMULATION_MODE:
        return {
            "scan_id": f"comp-{int(time.time())}",
            "status": "completed",
            "frameworks": {
                "SOC2": {"score": 85, "status": "compliant"},
                "ISO27001": {"score": 78, "status": "partial"},
                "GDPR": {"score": 92, "status": "compliant"},
                "HIPAA": {"score": 88, "status": "compliant"}
            },
            "recommendations": [
                "Enable additional encryption at rest",
                "Implement stronger access controls",
                "Add audit trail retention policy"
            ],
            "mode": "simulation"
        }
    
    raise HTTPException(status_code=503, detail="Live compliance scanning not configured")

@app.get("/threats/active")
async def get_active_threats(auth=Depends(verify_token)):
    audit_log("get_threats", auth.get("user", "anonymous"), auth.get("tenant", "default"), {})
    
    if SIMULATION_MODE:
        return {
            "threats": [
                {
                    "id": "threat-001",
                    "severity": "high",
                    "type": "brute_force",
                    "source": "192.168.1.100",
                    "target": "auth-api",
                    "detected_at": "2024-01-20T10:30:00Z",
                    "status": "blocked",
                    "mitigation": "IP blocked for 24 hours"
                },
                {
                    "id": "threat-002",
                    "severity": "medium",
                    "type": "suspicious_query",
                    "source": "internal",
                    "target": "data-api",
                    "detected_at": "2024-01-20T11:15:00Z",
                    "status": "monitoring",
                    "mitigation": "Query rate limited"
                }
            ],
            "summary": {
                "active": 2,
                "blocked": 1,
                "monitoring": 1
            },
            "mode": "simulation"
        }
    
    raise HTTPException(status_code=503, detail="Live threat detection not configured")

@app.post("/threats/report")
async def report_threat(alert: ThreatAlert, auth=Depends(verify_token)):
    audit_log("report_threat", auth.get("user", "anonymous"), auth.get("tenant", "default"), {
        "severity": alert.severity,
        "source": alert.source,
        "description": alert.description
    })
    
    threat_id = f"threat-{int(time.time())}"
    
    return {
        "threat_id": threat_id,
        "status": "received",
        "severity": alert.severity,
        "action_taken": "threat logged and analyzed",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/policies")
async def get_security_policies(auth=Depends(verify_token)):
    audit_log("get_policies", auth.get("user", "anonymous"), auth.get("tenant", "default"), {})
    
    if SIMULATION_MODE:
        return {
            "policies": [
                {
                    "id": "pol-001",
                    "name": "Authentication Policy",
                    "type": "access_control",
                    "rules": [
                        "Multi-factor authentication required",
                        "Password complexity: 12+ chars, mixed case, numbers, symbols",
                        "Session timeout: 8 hours"
                    ],
                    "status": "active"
                },
                {
                    "id": "pol-002",
                    "name": "Data Encryption Policy",
                    "type": "data_protection",
                    "rules": [
                        "AES-256 encryption for data at rest",
                        "TLS 1.3 for data in transit",
                        "Key rotation every 90 days"
                    ],
                    "status": "active"
                }
            ],
            "mode": "simulation"
        }
    
    raise HTTPException(status_code=503, detail="Live policy management not configured")

@app.post("/policies")
async def create_policy(policy: PolicyRule, auth=Depends(verify_token)):
    audit_log("create_policy", auth.get("user", "anonymous"), auth.get("tenant", "default"), {
        "name": policy.name,
        "condition": policy.condition,
        "action": policy.action
    })
    
    policy_id = f"pol-{int(time.time())}"
    
    return {
        "policy_id": policy_id,
        "name": policy.name,
        "status": "created",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/audit/logs")
async def get_audit_logs(limit: int = 100, auth=Depends(verify_token)):
    audit_log("get_audit_logs", auth.get("user", "anonymous"), auth.get("tenant", "default"), {"limit": limit})
    
    try:
        logs = []
        if os.path.exists("reports/logs/security_audit.log"):
            with open("reports/logs/security_audit.log", "r") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        logs.append(json.loads(line.strip()))
                    except:
                        continue
        
        return {
            "logs": logs,
            "count": len(logs),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "logs": [],
            "count": 0,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/metrics")
async def metrics():
    return """# HELP security_scans_total Total number of security scans
# TYPE security_scans_total counter
security_scans_total{type="vulnerability"} 42
security_scans_total{type="compliance"} 15

# HELP threats_detected_total Total number of threats detected
# TYPE threats_detected_total counter
threats_detected_total{severity="high"} 3
threats_detected_total{severity="medium"} 8
threats_detected_total{severity="low"} 12

# HELP policies_active Number of active security policies
# TYPE policies_active gauge
policies_active 25
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8019)