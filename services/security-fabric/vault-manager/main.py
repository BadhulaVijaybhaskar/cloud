from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any
import secrets

app = FastAPI(title="ATOM Vault Manager", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
COSIGN_KEY_PATH = os.getenv("COSIGN_KEY_PATH")

# In-memory key store for simulation
key_store = {
    "jwt_secret": {"value": "atom-jwt-secret", "rotated_at": datetime.utcnow().isoformat(), "age_days": 0},
    "cosign_key": {"value": "cosign-sim-key", "rotated_at": datetime.utcnow().isoformat(), "age_days": 0},
    "db_password": {"value": "db-secret", "rotated_at": datetime.utcnow().isoformat(), "age_days": 0}
}

def audit_log(action: str, details: Dict[str, Any]):
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "service": "vault-manager",
        "action": action,
        "details": details,
        "sha256": hashlib.sha256(json.dumps(details, sort_keys=True).encode()).hexdigest()
    }
    
    os.makedirs("reports/logs", exist_ok=True)
    with open("reports/logs/vault_audit.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

@app.get("/health")
async def health():
    vault_status = "connected" if VAULT_ADDR and VAULT_TOKEN else "simulation"
    cosign_status = "available" if COSIGN_KEY_PATH else "simulation"
    
    return {
        "status": "ok",
        "service": "vault-manager",
        "env": "SIM" if SIMULATION_MODE else "LIVE",
        "vault_status": vault_status,
        "cosign_status": cosign_status,
        "keys_managed": len(key_store),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/rotate")
async def rotate_secrets():
    if SIMULATION_MODE or not VAULT_ADDR:
        # Simulate key rotation
        rotated_keys = []
        for key_name, key_data in key_store.items():
            new_value = secrets.token_urlsafe(32)
            key_store[key_name] = {
                "value": new_value,
                "rotated_at": datetime.utcnow().isoformat(),
                "age_days": 0
            }
            rotated_keys.append(key_name)
        
        audit_log("rotate_secrets", {
            "keys_rotated": rotated_keys,
            "mode": "simulation"
        })
        
        return {
            "status": "completed",
            "keys_rotated": rotated_keys,
            "rotation_id": f"rot-{int(time.time())}",
            "mode": "simulation",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Live mode would integrate with actual Vault
    raise HTTPException(status_code=503, detail="Live Vault integration not configured")

@app.get("/status")
async def get_key_status():
    key_statuses = {}
    
    for key_name, key_data in key_store.items():
        rotated_at = datetime.fromisoformat(key_data["rotated_at"])
        age_days = (datetime.utcnow() - rotated_at).days
        
        key_statuses[key_name] = {
            "age_days": age_days,
            "rotated_at": key_data["rotated_at"],
            "needs_rotation": age_days > 90,
            "status": "healthy" if age_days <= 90 else "needs_rotation"
        }
    
    audit_log("get_status", {"keys_checked": list(key_statuses.keys())})
    
    return {
        "keys": key_statuses,
        "summary": {
            "total_keys": len(key_statuses),
            "healthy": len([k for k in key_statuses.values() if not k["needs_rotation"]]),
            "needs_rotation": len([k for k in key_statuses.values() if k["needs_rotation"]])
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
async def metrics():
    healthy_keys = len([k for k in key_store.values() if (datetime.utcnow() - datetime.fromisoformat(k["rotated_at"])).days <= 90])
    old_keys = len(key_store) - healthy_keys
    
    return f"""# HELP vault_keys_total Total number of managed keys
# TYPE vault_keys_total gauge
vault_keys_total {len(key_store)}

# HELP vault_keys_healthy Number of healthy keys (age <= 90 days)
# TYPE vault_keys_healthy gauge
vault_keys_healthy {healthy_keys}

# HELP vault_keys_old Number of keys needing rotation (age > 90 days)
# TYPE vault_keys_old gauge
vault_keys_old {old_keys}

# HELP vault_rotations_total Total number of key rotations
# TYPE vault_rotations_total counter
vault_rotations_total 1
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8101)