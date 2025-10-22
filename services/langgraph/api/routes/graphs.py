from fastapi import APIRouter
from typing import List, Dict, Any
from main import orchestrator

router = APIRouter(prefix="/v1/graphs", tags=["graphs"])

@router.get("/")
async def list_graphs() -> List[str]:
    """List available graph definitions"""
    return list(orchestrator.graphs.keys())

@router.get("/{graph_name}")
async def get_graph(graph_name: str) -> Dict[str, Any]:
    """Get graph definition"""
    if graph_name not in orchestrator.graphs:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    return orchestrator.graphs[graph_name]