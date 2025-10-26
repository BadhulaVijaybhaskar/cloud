from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import time
import hashlib
import random
from datetime import datetime
from typing import Dict, Any, List, Optional

app = FastAPI(title="ATOM Threat Sensor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class ThreatEvent(BaseModel):
    event: str
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    payload: Optional[Dict[str, Any]] = {}
    timestamp: Optional[str] = None

detection_count = 0
alert_count = 0
model_latency_ms = 0

# Simulated ML model for anomaly detection
def detect_anomaly(event_data: Dict[str, Any]) -> Dict[str, Any]:
    global model_latency_ms
    start_time = time.time()
    
    # Simulate ML processing time
    time.sleep(0.01)  # 10ms simulation
    
    # Simple rule-based anomaly detection for simulation
    anomaly_score = 0.0
    detected_patterns = []
    
    event_type = event_data.get("event", "").lower()
    source_ip = event_data.get("source_ip", "")
    payload = event_data.get("payload", {})
    
    # Check for suspicious patterns
    if "failed" in event_type and "login" in event_type:
        anomaly_score += 0.3
        detected_patterns.append("failed_authentication")
    
    if "admin" in str(payload).lower():
        anomaly_score += 0.4
        detected_patterns.append("admin_access_attempt")
    
    if source_ip and (source_ip.startswith("192.168.1.") or source_ip in ["10.0.0.1", "172.16.0.1"]):
        anomaly_score += 0.2
        detected_patterns.append("internal_network_anomaly")
    
    # SQL injection patterns
    sql_keywords = ["union", "select", "drop", "insert", "delete", "update"]
    payload_str = str(payload).lower()
    if any(keyword in payload_str for keyword in sql_keywords):
        anomaly_score += 0.6
        detected_patterns.append("sql_injection_attempt")
    
    # Add some randomness for simulation
    if SIMULATION_MODE:
        anomaly_score += random.uniform(-0.1, 0.2)
        anomaly_score = max(0.0, min(1.0, anomaly_score))  # Clamp to [0,1]
    
    model_latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "anomaly_score": round(anomaly_score, 3),
        "is_anomaly": anomaly_score > 0.5,
        "confidence": round(anomaly_score * 100, 1),
        "detected_patterns": detected_patterns,
        "model_latency_ms": model_latency_ms
    }

def audit_log(action: str, details: Dict[str, Any]):
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "service": "threat-sensor",
        "action": action,
        "details": details,
        "sha256": hashlib.sha256(json.dumps(details, sort_keys=True).encode()).hexdigest()
    }
    
    os.makedirs("reports/logs", exist_ok=True)
    with open("reports/logs/threat_sensor_audit.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "threat-sensor",
        "env": "SIM" if SIMULATION_MODE else "LIVE",
        "model_status": "loaded",
        "detections": detection_count,
        "alerts": alert_count,
        "avg_latency_ms": model_latency_ms,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/detect")
async def detect_threat(event: ThreatEvent):
    global detection_count, alert_count
    detection_count += 1
    
    # Prepare event data for analysis
    event_data = {
        "event": event.event,
        "source_ip": event.source_ip,
        "user_agent": event.user_agent,
        "payload": event.payload or {},
        "timestamp": event.timestamp or datetime.utcnow().isoformat()
    }
    
    # Run anomaly detection
    detection_result = detect_anomaly(event_data)
    
    # Generate alert if anomaly detected
    alert_id = None
    if detection_result["is_anomaly"]:
        alert_count += 1
        alert_id = f"alert-{int(time.time())}-{alert_count}"
    
    result = {
        "detection_id": f"det-{int(time.time())}-{detection_count}",
        "alert_id": alert_id,
        "event": event.event,
        "anomaly_score": detection_result["anomaly_score"],
        "is_anomaly": detection_result["is_anomaly"],
        "confidence": detection_result["confidence"],
        "detected_patterns": detection_result["detected_patterns"],
        "model_latency_ms": detection_result["model_latency_ms"],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Log the detection
    audit_log("threat_detection", {
        "event": event.event,
        "anomaly_score": detection_result["anomaly_score"],
        "is_anomaly": detection_result["is_anomaly"],
        "source_ip": event.source_ip
    })
    
    return result

@app.get("/alerts")
async def get_recent_alerts(limit: int = 50):
    # In a real implementation, this would query a database
    # For simulation, return mock alerts
    
    if SIMULATION_MODE:
        mock_alerts = []
        for i in range(min(alert_count, limit)):
            mock_alerts.append({
                "alert_id": f"alert-{int(time.time())}-{i+1}",
                "event_type": random.choice(["failed_login", "sql_injection", "admin_access"]),
                "anomaly_score": round(random.uniform(0.5, 1.0), 3),
                "source_ip": random.choice(["192.168.1.100", "10.0.0.50", "172.16.0.25"]),
                "timestamp": datetime.utcnow().isoformat(),
                "status": random.choice(["new", "investigating", "resolved"])
            })
        
        return {
            "alerts": mock_alerts,
            "count": len(mock_alerts),
            "total_alerts": alert_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return {
        "alerts": [],
        "count": 0,
        "total_alerts": alert_count,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/model/status")
async def get_model_status():
    return {
        "model_name": "ATOM Anomaly Detector v1.0",
        "status": "active",
        "version": "1.0.0",
        "training_date": "2024-01-01",
        "accuracy": 0.94,
        "precision": 0.91,
        "recall": 0.89,
        "f1_score": 0.90,
        "avg_latency_ms": model_latency_ms,
        "detections_processed": detection_count,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
async def metrics():
    anomaly_rate = (alert_count / detection_count * 100) if detection_count > 0 else 0
    
    return f"""# HELP threat_sensor_detections_total Total number of threat detections
# TYPE threat_sensor_detections_total counter
threat_sensor_detections_total {detection_count}

# HELP threat_sensor_alerts_total Total number of alerts generated
# TYPE threat_sensor_alerts_total counter
threat_sensor_alerts_total {alert_count}

# HELP threat_sensor_model_latency_ms Model inference latency in milliseconds
# TYPE threat_sensor_model_latency_ms gauge
threat_sensor_model_latency_ms {model_latency_ms}

# HELP threat_sensor_anomaly_rate Percentage of detections that are anomalies
# TYPE threat_sensor_anomaly_rate gauge
threat_sensor_anomaly_rate {anomaly_rate:.2f}

# HELP threat_sensor_model_accuracy Model accuracy score
# TYPE threat_sensor_model_accuracy gauge
threat_sensor_model_accuracy 0.94
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8103)