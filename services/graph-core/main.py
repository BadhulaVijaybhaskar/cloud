#!/usr/bin/env python3
import os
import json
import logging
import hashlib
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Optional

app = FastAPI(title="Graph Core Service")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class GraphNode(BaseModel):
    type: str
    data: Dict[str, Any]
    meta: Optional[Dict[str, Any]] = {}
    tenant: str = "default"

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    confidence: float = 1.0
    tenant: str = "default"

# In-memory storage for simulation
graph_nodes = {}
graph_edges = {}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "graph-core", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {
        "nodes_total": len(graph_nodes),
        "edges_total": len(graph_edges),
        "tenants_active": len(set(n.get("tenant") for n in graph_nodes.values())),
        "avg_node_degree": 2.5,
        "simulation": SIMULATION_MODE
    }

@app.post("/graph/node")
async def create_node(node: GraphNode):
    if SIMULATION_MODE:
        # Generate node ID and hash for immutability
        node_data = json.dumps(node.data, sort_keys=True)
        node_hash = hashlib.sha256(node_data.encode()).hexdigest()[:16]
        node_id = f"{node.type}-{node_hash}"
        
        graph_node = {
            "id": node_id,
            "type": node.type,
            "data": node.data,
            "meta": node.meta,
            "tenant": node.tenant,
            "hash": node_hash,
            "created_at": "2024-01-15T10:30:00Z",
            "edges_in": [],
            "edges_out": []
        }
        
        graph_nodes[node_id] = graph_node
        
        logger.info(f"Graph node created: {node_id} (type: {node.type}, tenant: {node.tenant})")
        return {
            "status": "created",
            "node_id": node_id,
            "hash": node_hash,
            "simulation": True
        }
    
    return {"status": "error", "message": "Graph database required"}

@app.post("/graph/edge")
async def create_edge(edge: GraphEdge):
    if SIMULATION_MODE:
        # Verify source and target nodes exist
        if edge.source not in graph_nodes or edge.target not in graph_nodes:
            return {"status": "error", "message": "Source or target node not found"}
        
        edge_id = f"{edge.source}-{edge.relation}-{edge.target}"
        
        graph_edge = {
            "id": edge_id,
            "source": edge.source,
            "target": edge.target,
            "relation": edge.relation,
            "confidence": edge.confidence,
            "tenant": edge.tenant,
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        graph_edges[edge_id] = graph_edge
        
        # Update node edge lists
        graph_nodes[edge.source]["edges_out"].append(edge_id)
        graph_nodes[edge.target]["edges_in"].append(edge_id)
        
        logger.info(f"Graph edge created: {edge_id} (confidence: {edge.confidence})")
        return {
            "status": "created",
            "edge_id": edge_id,
            "confidence": edge.confidence,
            "simulation": True
        }
    
    return {"status": "error", "message": "Graph database required"}

@app.get("/graph/{node_id}")
async def get_node(node_id: str):
    if SIMULATION_MODE:
        if node_id in graph_nodes:
            node = graph_nodes[node_id].copy()
            
            # Add connected edges information
            node["connected_edges"] = {
                "incoming": len(node["edges_in"]),
                "outgoing": len(node["edges_out"]),
                "total_degree": len(node["edges_in"]) + len(node["edges_out"])
            }
            
            return node
        
        return {"status": "not_found", "node_id": node_id}
    
    return {"status": "error", "message": "Graph database required"}

@app.get("/graph/neighbors/{node_id}")
async def get_neighbors(node_id: str):
    if SIMULATION_MODE:
        if node_id not in graph_nodes:
            return {"status": "not_found", "node_id": node_id}
        
        neighbors = []
        node = graph_nodes[node_id]
        
        # Get neighbors from outgoing edges
        for edge_id in node["edges_out"]:
            edge = graph_edges[edge_id]
            target_node = graph_nodes[edge["target"]]
            neighbors.append({
                "node_id": edge["target"],
                "type": target_node["type"],
                "relation": edge["relation"],
                "confidence": edge["confidence"],
                "direction": "outgoing"
            })
        
        # Get neighbors from incoming edges
        for edge_id in node["edges_in"]:
            edge = graph_edges[edge_id]
            source_node = graph_nodes[edge["source"]]
            neighbors.append({
                "node_id": edge["source"],
                "type": source_node["type"],
                "relation": edge["relation"],
                "confidence": edge["confidence"],
                "direction": "incoming"
            })
        
        return {
            "node_id": node_id,
            "neighbors": neighbors,
            "neighbor_count": len(neighbors),
            "simulation": True
        }
    
    return {"status": "error", "message": "Graph database required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9101)