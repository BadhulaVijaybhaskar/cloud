from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

app = FastAPI(title="Federated Context Router", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
GLOBAL_REGISTRY_URL = os.getenv("GLOBAL_REGISTRY_URL", "http://localhost:8080")

class ContextUpdate(BaseModel):
    entity_id: str
    context_data: Dict[str, Any]
    target_regions: List[str]
    signature: str
    tenant_id: str

class RoutingResult(BaseModel):
    entity_id: str
    routed_regions: List[str]
    failed_regions: List[str]
    routing_hash: str

# Mock region registry
region_registry = {
    "us-east-1": {"url": "http://us-east-1.context.local", "status": "active"},
    "eu-west-1": {"url": "http://eu-west-1.context.local", "status": "active"},
    "ap-south-1": {"url": "http://ap-south-1.context.local", "status": "active"}
}

routing_log = {}

@app.get("/health")
async def health():
    return {"status": "healthy", "simulation_mode": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {
        "active_regions": len([r for r in region_registry.values() if r["status"] == "active"]),
        "routing_operations": len(routing_log),
        "simulation_mode": SIMULATION_MODE
    }

@app.post("/route/context")
async def route_context_update(update: ContextUpdate):
    """Route contextual updates to nearest regions"""
    try:
        # Validate signature (mock validation in simulation mode)
        if SIMULATION_MODE:
            # Mock signature validation
            expected_sig = hashlib.sha256(f"{update.entity_id}{update.tenant_id}".encode()).hexdigest()[:16]
            if update.signature != expected_sig:
                logger.warning(f"Signature mismatch for {update.entity_id} (simulation)")
        
        routed_regions = []
        failed_regions = []
        
        for region in update.target_regions:
            if region in region_registry and region_registry[region]["status"] == "active":
                if SIMULATION_MODE:
                    # Mock successful routing
                    routed_regions.append(region)
                    logger.info(f"Routed context for {update.entity_id} to {region} (simulation)")
                else:
                    # Real implementation would make HTTP calls to regional endpoints
                    try:
                        # Mock HTTP call
                        routed_regions.append(region)
                    except Exception as e:
                        failed_regions.append(region)
                        logger.error(f"Failed to route to {region}: {e}")
            else:
                failed_regions.append(region)
                logger.warning(f"Region {region} not available")
        
        # Generate routing hash
        routing_data = {
            "entity_id": update.entity_id,
            "routed_regions": sorted(routed_regions),
            "timestamp": datetime.utcnow().isoformat()
        }
        routing_hash = hashlib.sha256(json.dumps(routing_data, sort_keys=True).encode()).hexdigest()[:16]
        
        # Log routing operation
        routing_log[f"{update.tenant_id}:{update.entity_id}"] = {
            "routed_regions": routed_regions,
            "failed_regions": failed_regions,
            "timestamp": datetime.utcnow().isoformat(),
            "routing_hash": routing_hash
        }
        
        return RoutingResult(
            entity_id=update.entity_id,
            routed_regions=routed_regions,
            failed_regions=failed_regions,
            routing_hash=routing_hash
        )
        
    except Exception as e:
        logger.error(f"Routing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/route/regions")
async def get_available_regions():
    """Get list of available regions"""
    active_regions = {
        region: info for region, info in region_registry.items()
        if info["status"] == "active"
    }
    
    return {
        "regions": active_regions,
        "total_count": len(active_regions)
    }

@app.get("/route/nearest/{entity_id}")
async def find_nearest_region(entity_id: str, tenant_id: str, user_region: Optional[str] = None):
    """Find nearest region for context routing"""
    # Mock region selection logic
    if user_region and user_region in region_registry:
        nearest = user_region
    else:
        # Default to us-east-1 for simulation
        nearest = "us-east-1"
    
    return {
        "entity_id": entity_id,
        "tenant_id": tenant_id,
        "nearest_region": nearest,
        "region_url": region_registry[nearest]["url"],
        "latency_estimate_ms": 50  # Mock latency
    }

@app.post("/route/tenant-isolation")
async def validate_tenant_isolation(entity_id: str, tenant_id: str, target_tenant: str):
    """Validate tenant isolation for routing"""
    if tenant_id != target_tenant:
        raise HTTPException(status_code=403, detail="Cross-tenant routing not allowed")
    
    return {
        "entity_id": entity_id,
        "tenant_id": tenant_id,
        "isolation_valid": True,
        "validation_timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9103)