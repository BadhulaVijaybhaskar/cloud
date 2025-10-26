from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import jwt
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

app = FastAPI(title="ATOM Trust Proxy", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
JWT_SECRET = os.getenv("JWT_SECRET", "atom-trust-proxy-secret")
TLS_CERT_PATH = os.getenv("TLS_CERT_PATH")
TLS_KEY_PATH = os.getenv("TLS_KEY_PATH")

verification_count = 0
blocked_requests = 0

def audit_log(action: str, details: Dict[str, Any]):
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "service": "trust-proxy",
        "action": action,
        "details": details,
        "sha256": hashlib.sha256(json.dumps(details, sort_keys=True).encode()).hexdigest()
    }
    
    os.makedirs("reports/logs", exist_ok=True)
    with open("reports/logs/trust_proxy_audit.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

@app.get("/health")
async def health():
    tls_status = "configured" if TLS_CERT_PATH and TLS_KEY_PATH else "simulation"
    
    return {
        "status": "ok",
        "service": "trust-proxy",
        "env": "SIM" if SIMULATION_MODE else "LIVE",
        "tls_status": tls_status,
        "verifications": verification_count,
        "blocked": blocked_requests,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/verify")
async def verify_request(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_client_cert: Optional[str] = Header(None)
):
    global verification_count, blocked_requests
    verification_count += 1
    
    client_ip = request.client.host if request.client else "unknown"
    
    # JWT Verification
    jwt_valid = False
    jwt_payload = {}
    
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.split(" ")[1]
            jwt_payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            jwt_valid = True
        except jwt.InvalidTokenError:
            jwt_valid = False
    
    # mTLS Verification (simulated)
    mtls_valid = False
    if SIMULATION_MODE:
        # Simulate mTLS validation
        mtls_valid = x_client_cert is not None or client_ip in ["127.0.0.1", "localhost"]
    else:
        # In live mode, would verify actual client certificates
        mtls_valid = TLS_CERT_PATH and TLS_KEY_PATH and x_client_cert
    
    # Overall verification result
    verified = jwt_valid and mtls_valid
    
    if not verified:
        blocked_requests += 1
    
    verification_result = {
        "verified": verified,
        "jwt_valid": jwt_valid,
        "mtls_valid": mtls_valid,
        "client_ip": client_ip,
        "user": jwt_payload.get("user", "anonymous"),
        "tenant": jwt_payload.get("tenant", "default"),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    audit_log("verify_request", {
        "verified": verified,
        "client_ip": client_ip,
        "user": jwt_payload.get("user", "anonymous")
    })
    
    if not verified:
        raise HTTPException(status_code=403, detail="Access denied: Invalid JWT or mTLS")
    
    return verification_result

@app.post("/validate-token")
async def validate_token(authorization: str = Header(...)):
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=400, detail="Invalid authorization header format")
        
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        
        audit_log("validate_token", {
            "user": payload.get("user", "unknown"),
            "tenant": payload.get("tenant", "default"),
            "valid": True
        })
        
        return {
            "valid": True,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except jwt.InvalidTokenError as e:
        audit_log("validate_token", {
            "valid": False,
            "error": str(e)
        })
        
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

@app.get("/metrics")
async def metrics():
    success_rate = ((verification_count - blocked_requests) / verification_count * 100) if verification_count > 0 else 100
    
    return f"""# HELP trust_proxy_verifications_total Total number of verification requests
# TYPE trust_proxy_verifications_total counter
trust_proxy_verifications_total {verification_count}

# HELP trust_proxy_blocked_total Total number of blocked requests
# TYPE trust_proxy_blocked_total counter
trust_proxy_blocked_total {blocked_requests}

# HELP trust_proxy_success_rate Success rate of verifications
# TYPE trust_proxy_success_rate gauge
trust_proxy_success_rate {success_rate:.2f}

# HELP trust_proxy_jwt_validations_total JWT validation attempts
# TYPE trust_proxy_jwt_validations_total counter
trust_proxy_jwt_validations_total {verification_count}

# HELP trust_proxy_mtls_validations_total mTLS validation attempts
# TYPE trust_proxy_mtls_validations_total counter
trust_proxy_mtls_validations_total {verification_count}
"""

if __name__ == "__main__":
    import uvicorn
    
    # Use HTTPS in live mode if certificates are available
    if not SIMULATION_MODE and TLS_CERT_PATH and TLS_KEY_PATH:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8102,
            ssl_keyfile=TLS_KEY_PATH,
            ssl_certfile=TLS_CERT_PATH
        )
    else:
        uvicorn.run(app, host="0.0.0.0", port=8102)