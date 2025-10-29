#!/usr/bin/env python3
import os
import json
import logging
from fastapi import FastAPI
from typing import Dict, Any, List

app = FastAPI(title="Semantic Reasoner")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

# In-memory storage for simulation
inference_cache = {}
reasoning_rules = []

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "semantic-reasoner", "simulation": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {
        "inferences_generated": len(inference_cache),
        "reasoning_rules": len(reasoning_rules),
        "avg_confidence": 0.82,
        "inference_accuracy": 0.89,
        "simulation": SIMULATION_MODE
    }

@app.post("/reasoner/infer")
async def infer_relationships(inference_request: dict):
    if SIMULATION_MODE:
        graph_data = inference_request.get("graph_data", {})
        confidence_threshold = inference_request.get("confidence_threshold", 0.8)
        
        # Simulate semantic reasoning
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        inferred_edges = []
        
        # Simulate different types of inferences
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes[i+1:], i+1):
                # Simulate type-based inference
                if node1.get("type") == "model" and node2.get("type") == "data":
                    confidence = 0.85
                    inferred_edges.append({
                        "source": node1["id"],
                        "target": node2["id"],
                        "relation": "trained_on",
                        "confidence": confidence,
                        "inference_type": "type_based",
                        "reasoning": f"Model {node1['id']} likely trained on data {node2['id']}"
                    })
                
                # Simulate temporal inference
                elif "timestamp" in node1.get("meta", {}) and "timestamp" in node2.get("meta", {}):
                    confidence = 0.75
                    inferred_edges.append({
                        "source": node1["id"],
                        "target": node2["id"],
                        "relation": "temporal_successor",
                        "confidence": confidence,
                        "inference_type": "temporal",
                        "reasoning": f"Temporal relationship inferred between {node1['id']} and {node2['id']}"
                    })
        
        # Filter by confidence threshold
        high_confidence_edges = [e for e in inferred_edges if e["confidence"] >= confidence_threshold]
        
        inference_id = f"inf-{hash(str(graph_data)) % 10000}"
        inference_result = {
            "inference_id": inference_id,
            "inferred_edges": high_confidence_edges,
            "total_inferences": len(inferred_edges),
            "high_confidence_inferences": len(high_confidence_edges),
            "confidence_threshold": confidence_threshold,
            "reasoning_steps": [
                "Analyzed node types for semantic relationships",
                "Applied temporal reasoning rules",
                "Filtered by confidence threshold"
            ],
            "simulation": True
        }
        
        inference_cache[inference_id] = inference_result
        
        logger.info(f"Semantic inference complete: {len(high_confidence_edges)} high-confidence edges")
        return inference_result
    
    return {"status": "error", "message": "Semantic reasoning infrastructure required"}

@app.post("/reasoner/rules/add")
async def add_reasoning_rule(rule_data: dict):
    if SIMULATION_MODE:
        rule_id = f"rule-{len(reasoning_rules) + 1}"
        
        reasoning_rule = {
            "rule_id": rule_id,
            "name": rule_data.get("name", "Custom Rule"),
            "conditions": rule_data.get("conditions", []),
            "conclusions": rule_data.get("conclusions", []),
            "confidence_weight": rule_data.get("confidence_weight", 0.8),
            "created_at": "2024-01-15T10:30:00Z",
            "active": True
        }
        
        reasoning_rules.append(reasoning_rule)
        
        return {
            "status": "added",
            "rule_id": rule_id,
            "confidence_weight": reasoning_rule["confidence_weight"],
            "simulation": True
        }
    
    return {"status": "error", "message": "Rule storage required"}

@app.get("/reasoner/rules")
async def list_reasoning_rules():
    if SIMULATION_MODE:
        return {
            "rules": reasoning_rules,
            "total": len(reasoning_rules),
            "active_rules": len([r for r in reasoning_rules if r["active"]]),
            "simulation": True
        }
    
    return {"status": "error", "message": "Rule storage required"}

@app.post("/reasoner/explain")
async def explain_inference(explanation_request: dict):
    if SIMULATION_MODE:
        inference_id = explanation_request.get("inference_id")
        edge_id = explanation_request.get("edge_id")
        
        if inference_id in inference_cache:
            inference = inference_cache[inference_id]
            
            # Find the specific edge
            target_edge = None
            for edge in inference["inferred_edges"]:
                if f"{edge['source']}-{edge['target']}" == edge_id:
                    target_edge = edge
                    break
            
            if target_edge:
                explanation = {
                    "edge_id": edge_id,
                    "inference_id": inference_id,
                    "explanation": {
                        "reasoning_type": target_edge["inference_type"],
                        "confidence": target_edge["confidence"],
                        "evidence": target_edge["reasoning"],
                        "rules_applied": ["type_similarity", "temporal_analysis"],
                        "alternative_interpretations": [
                            "Could be coincidental relationship",
                            "May require additional validation"
                        ]
                    },
                    "human_readable": f"The relationship '{target_edge['relation']}' between {target_edge['source']} and {target_edge['target']} was inferred with {target_edge['confidence']:.2f} confidence based on {target_edge['inference_type']} analysis.",
                    "simulation": True
                }
                
                return explanation
        
        return {"status": "not_found", "inference_id": inference_id, "edge_id": edge_id}
    
    return {"status": "error", "message": "Explanation infrastructure required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9104)