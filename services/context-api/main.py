from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

app = FastAPI(title="Context API Gateway", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class ContextQuery(BaseModel):
    entity_id: Optional[str] = None
    time_range: Optional[Dict[str, str]] = None
    region: Optional[str] = None
    relevance_threshold: Optional[float] = 0.5
    tenant_id: str

class ContextResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_count: int
    query_time_ms: int
    relevance_scores: Dict[str, float]

# Mock context data store
context_data = {
    "tenant1:user123": {
        "entity_id": "user123",
        "context": {
            "location": "us-east-1",
            "activity": "browsing",
            "preferences": {"theme": "dark", "language": "en"},
            "session_duration": 1800
        },
        "relevance": 0.85,
        "last_updated": "2024-12-28T10:00:00Z",
        "region": "us-east-1"
    },
    "tenant1:project456": {
        "entity_id": "project456",
        "context": {
            "status": "active",
            "team_size": 5,
            "deployment_region": "eu-west-1",
            "resource_usage": {"cpu": 0.65, "memory": 0.78}
        },
        "relevance": 0.92,
        "last_updated": "2024-12-28T09:45:00Z",
        "region": "eu-west-1"
    }
}

@app.get("/health")
async def health():
    return {"status": "healthy", "simulation_mode": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {
        "cached_contexts": len(context_data),
        "simulation_mode": SIMULATION_MODE,
        "avg_query_time_ms": 45
    }

@app.post("/context/query")
async def query_context(query: ContextQuery):
    """Unified query interface for contextual insights"""
    start_time = datetime.utcnow()
    
    try:
        results = []
        relevance_scores = {}
        
        # Filter context data based on query parameters
        for key, context_item in context_data.items():
            tenant_id, entity_id = key.split(":", 1)
            
            # Tenant isolation
            if tenant_id != query.tenant_id:
                continue
            
            # Entity filter
            if query.entity_id and entity_id != query.entity_id:
                continue
            
            # Region filter
            if query.region and context_item.get("region") != query.region:
                continue
            
            # Relevance threshold filter
            if context_item.get("relevance", 0) < query.relevance_threshold:
                continue
            
            # Time range filter
            if query.time_range:
                item_time = datetime.fromisoformat(context_item["last_updated"].replace('Z', '+00:00'))
                start_time_filter = datetime.fromisoformat(query.time_range.get("start", "2024-01-01T00:00:00Z").replace('Z', '+00:00'))
                end_time_filter = datetime.fromisoformat(query.time_range.get("end", "2024-12-31T23:59:59Z").replace('Z', '+00:00'))
                
                if not (start_time_filter <= item_time <= end_time_filter):
                    continue
            
            # Add to results
            results.append({
                "entity_id": entity_id,
                "context": context_item["context"],
                "last_updated": context_item["last_updated"],
                "region": context_item.get("region"),
                "relevance": context_item.get("relevance")
            })
            
            relevance_scores[entity_id] = context_item.get("relevance", 0.5)
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        query_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        logger.info(f"Context query returned {len(results)} results in {query_time_ms}ms")
        
        return ContextResponse(
            results=results,
            total_count=len(results),
            query_time_ms=query_time_ms,
            relevance_scores=relevance_scores
        )
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/context/entity/{entity_id}")
async def get_entity_context(entity_id: str, tenant_id: str):
    """Get context for specific entity"""
    key = f"{tenant_id}:{entity_id}"
    
    if key not in context_data:
        raise HTTPException(status_code=404, detail="Entity context not found")
    
    context_item = context_data[key]
    
    return {
        "entity_id": entity_id,
        "tenant_id": tenant_id,
        "context": context_item["context"],
        "metadata": {
            "last_updated": context_item["last_updated"],
            "region": context_item.get("region"),
            "relevance": context_item.get("relevance")
        }
    }

@app.get("/context/search")
async def search_context(
    q: str = Query(..., description="Search query"),
    tenant_id: str = Query(..., description="Tenant ID"),
    limit: int = Query(10, description="Result limit")
):
    """Search context data"""
    results = []
    
    # Simple text search in context data
    for key, context_item in context_data.items():
        tenant_id_key, entity_id = key.split(":", 1)
        
        if tenant_id_key != tenant_id:
            continue
        
        # Search in context values
        context_str = json.dumps(context_item["context"]).lower()
        if q.lower() in context_str or q.lower() in entity_id.lower():
            results.append({
                "entity_id": entity_id,
                "context": context_item["context"],
                "relevance": context_item.get("relevance", 0.5),
                "match_score": 0.8  # Mock match score
            })
    
    # Sort by relevance and limit results
    results.sort(key=lambda x: x["relevance"], reverse=True)
    results = results[:limit]
    
    return {
        "query": q,
        "tenant_id": tenant_id,
        "results": results,
        "total_matches": len(results)
    }

@app.get("/context/regions")
async def get_context_by_region(tenant_id: str):
    """Get context distribution by region"""
    region_stats = {}
    
    for key, context_item in context_data.items():
        tenant_id_key, entity_id = key.split(":", 1)
        
        if tenant_id_key != tenant_id:
            continue
        
        region = context_item.get("region", "unknown")
        
        if region not in region_stats:
            region_stats[region] = {
                "entity_count": 0,
                "avg_relevance": 0,
                "entities": []
            }
        
        region_stats[region]["entity_count"] += 1
        region_stats[region]["entities"].append(entity_id)
        region_stats[region]["avg_relevance"] = (
            region_stats[region]["avg_relevance"] + context_item.get("relevance", 0.5)
        ) / region_stats[region]["entity_count"]
    
    return {
        "tenant_id": tenant_id,
        "region_distribution": region_stats,
        "total_regions": len(region_stats)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9105)