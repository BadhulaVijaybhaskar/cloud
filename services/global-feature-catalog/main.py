#!/usr/bin/env python3
import os
import json
import logging
import hashlib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

app = FastAPI(title="Global Feature Catalog")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class FeatureRegistration(BaseModel):
    tenant: str
    feature_id: str
    schema: Dict[str, Any]
    fingerprint: str = None
    consented: bool = True

# In-memory storage for simulation
feature_store = {}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "global-feature-catalog", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {
        "features_registered": len(feature_store),
        "tenants_active": len(set(f.get("tenant") for f in feature_store.values())),
        "consent_rate": 0.95,
        "simulation": SIMULATION_MODE
    }

@app.post("/features/register")
async def register_feature(req: FeatureRegistration):
    if SIMULATION_MODE:
        # Generate fingerprint if not provided
        if not req.fingerprint:
            schema_str = json.dumps(req.schema, sort_keys=True)
            req.fingerprint = hashlib.sha256(schema_str.encode()).hexdigest()[:16]
        
        feature_key = f"{req.tenant}:{req.feature_id}"
        
        feature_record = {
            "tenant": req.tenant,
            "feature_id": req.feature_id,
            "schema": req.schema,
            "fingerprint": req.fingerprint,
            "consented": req.consented,
            "registered_at": "2024-01-15T10:30:00Z",
            "status": "active" if req.consented else "pending_consent"
        }
        
        feature_store[feature_key] = feature_record
        
        logger.info(f"Feature registered: {feature_key} (consented: {req.consented})")
        return {
            "status": "registered",
            "feature_key": feature_key,
            "fingerprint": req.fingerprint,
            "consented": req.consented,
            "simulation": True
        }
    
    return {"status": "error", "message": "Feature catalog infrastructure required"}

@app.get("/features/{tenant}")
async def list_features(tenant: str):
    if SIMULATION_MODE:
        tenant_features = [
            f for f in feature_store.values() 
            if f["tenant"] == tenant
        ]
        
        return {
            "tenant": tenant,
            "features": tenant_features,
            "count": len(tenant_features),
            "simulation": True
        }
    
    return {"status": "error", "message": "Feature storage required"}

@app.get("/features/global/catalog")
async def get_global_catalog():
    if SIMULATION_MODE:
        # Anonymized global view
        catalog = {}
        for feature in feature_store.values():
            if feature["consented"]:
                schema_type = feature["schema"].get("type", "unknown")
                if schema_type not in catalog:
                    catalog[schema_type] = {"count": 0, "fingerprints": []}
                catalog[schema_type]["count"] += 1
                catalog[schema_type]["fingerprints"].append(feature["fingerprint"])
        
        return {
            "global_catalog": catalog,
            "total_consented_features": sum(c["count"] for c in catalog.values()),
            "simulation": True
        }
    
    return {"status": "error", "message": "Global catalog infrastructure required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)