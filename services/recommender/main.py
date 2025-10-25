#!/usr/bin/env python3
"""
NeuralOps Recommendation API
Provides WPK recommendations based on incident signals and historical data.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
import numpy as np

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
recommendations_total = Counter('neuralops_recommendations_total', 'Total recommendations generated', ['method'])
recommendation_duration = Histogram('neuralops_recommendation_duration_seconds', 'Recommendation generation time')

app = FastAPI(title="NeuralOps Recommender", version="1.0.0")

class RecommendRequest(BaseModel):
    signal_id: Optional[str] = None
    incident_description: Optional[str] = None
    labels: Dict[str, str] = {}
    limit: int = 5

class Recommendation(BaseModel):
    playbook_id: str
    score: float
    justification: str
    confidence: float
    metadata: Dict[str, Any] = {}

class RecommendResponse(BaseModel):
    recommendations: List[Recommendation]
    total_candidates: int
    method: str
    timestamp: str

class RecommenderEngine:
    """Core recommendation engine."""
    
    def __init__(self):
        self.vectors_file = "reports/test_vectors_local.json"
        self.signals_db = "insight_signals.db"
        self.playbooks = self._load_playbooks()
        self.vectors = self._load_vectors()
        
    def _load_playbooks(self) -> List[Dict[str, Any]]:
        """Load available playbooks."""
        # Sample playbooks based on existing examples
        return [
            {
                "id": "backup-verify",
                "name": "Backup Verification",
                "description": "Verify backup integrity and restore capability",
                "success_rate": 0.95,
                "avg_duration": 150,
                "tags": ["backup", "verification", "storage"],
                "safety_mode": "manual"
            },
            {
                "id": "restart-unhealthy",
                "name": "Restart Unhealthy Services",
                "description": "Restart services showing health check failures",
                "success_rate": 0.85,
                "avg_duration": 45,
                "tags": ["restart", "health", "recovery"],
                "safety_mode": "manual"
            },
            {
                "id": "scale-on-latency",
                "name": "Scale on High Latency",
                "description": "Auto-scale services experiencing high latency",
                "success_rate": 0.90,
                "avg_duration": 120,
                "tags": ["scaling", "performance", "latency"],
                "safety_mode": "auto"
            },
            {
                "id": "requeue-job",
                "name": "Requeue Failed Jobs",
                "description": "Requeue jobs that failed due to transient errors",
                "success_rate": 0.80,
                "avg_duration": 30,
                "tags": ["jobs", "retry", "queue"],
                "safety_mode": "manual"
            },
            {
                "id": "rotate-secret",
                "name": "Rotate Expired Secrets",
                "description": "Rotate secrets that are expired or compromised",
                "success_rate": 0.75,
                "avg_duration": 200,
                "tags": ["security", "secrets", "rotation"],
                "safety_mode": "manual"
            }
        ]
    
    def _load_vectors(self) -> Optional[Dict[str, Any]]:
        """Load vector embeddings if available."""
        try:
            if os.path.exists(self.vectors_file):
                with open(self.vectors_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load vectors: {e}")
        return None
    
    def recommend(self, request: RecommendRequest) -> RecommendResponse:
        """Generate recommendations for incident."""
        with recommendation_duration.time():
            try:
                # Get incident context
                incident_context = self._get_incident_context(request)
                
                # Generate recommendations
                if self.vectors and len(self.vectors.get("vectors", [])) > 0:
                    recommendations = self._vector_based_recommendations(incident_context, request.limit)
                    method = "vector_similarity"
                else:
                    recommendations = self._rule_based_recommendations(incident_context, request.limit)
                    method = "rule_based"
                
                # Record metrics
                recommendations_total.labels(method=method).inc()
                
                return RecommendResponse(
                    recommendations=recommendations,
                    total_candidates=len(self.playbooks),
                    method=method,
                    timestamp=datetime.utcnow().isoformat()
                )
                
            except Exception as e:
                logger.error(f"Recommendation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _get_incident_context(self, request: RecommendRequest) -> Dict[str, Any]:
        """Extract incident context from request."""
        context = {
            "description": request.incident_description or "",
            "labels": request.labels,
            "signal_data": None
        }
        
        # Get signal data if signal_id provided
        if request.signal_id:
            try:
                with sqlite3.connect(self.signals_db) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.execute(
                        "SELECT * FROM insight_signals WHERE id = ?",
                        (request.signal_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        context["signal_data"] = dict(row)
                        context["description"] = row["hint"]
                        if row["labels"]:
                            try:
                                context["labels"].update(json.loads(row["labels"]))
                            except json.JSONDecodeError:
                                pass
            except Exception as e:
                logger.warning(f"Could not load signal data: {e}")
        
        return context
    
    def _vector_based_recommendations(self, context: Dict[str, Any], limit: int) -> List[Recommendation]:
        """Generate recommendations using vector similarity."""
        recommendations = []
        
        try:
            # Create query vector from incident description
            query_text = context["description"]
            if not query_text:
                query_text = " ".join([f"{k}:{v}" for k, v in context["labels"].items()])
            
            # Simple text matching for now (would use actual embeddings in production)
            for playbook in self.playbooks:
                score = self._calculate_similarity_score(query_text, playbook)
                
                if score > 0.1:  # Minimum threshold
                    recommendations.append(Recommendation(
                        playbook_id=playbook["id"],
                        score=score,
                        justification=self._generate_justification(playbook, context, score),
                        confidence=min(0.9, score + 0.1),
                        metadata={
                            "success_rate": playbook["success_rate"],
                            "avg_duration": playbook["avg_duration"],
                            "safety_mode": playbook["safety_mode"]
                        }
                    ))
            
            # Sort by score and limit
            recommendations.sort(key=lambda x: x.score, reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Vector-based recommendation failed: {e}")
            return self._rule_based_recommendations(context, limit)
    
    def _rule_based_recommendations(self, context: Dict[str, Any], limit: int) -> List[Recommendation]:
        """Generate recommendations using rule-based matching."""
        recommendations = []
        
        description = context["description"].lower()
        labels = context["labels"]
        
        # Rule-based matching
        for playbook in self.playbooks:
            score = 0.0
            reasons = []
            
            # Tag matching
            for tag in playbook["tags"]:
                if tag in description:
                    score += 0.3
                    reasons.append(f"matches '{tag}' keyword")
            
            # Label matching
            for label_key, label_value in labels.items():
                if label_key.lower() in playbook["name"].lower():
                    score += 0.2
                    reasons.append(f"matches label '{label_key}'")
            
            # Specific patterns
            if "backup" in description and "backup" in playbook["tags"]:
                score += 0.4
                reasons.append("backup-related incident")
            
            if "unhealthy" in description and "health" in playbook["tags"]:
                score += 0.4
                reasons.append("health check failure detected")
            
            if "latency" in description and "performance" in playbook["tags"]:
                score += 0.4
                reasons.append("performance issue detected")
            
            if "failed" in description and "retry" in playbook["tags"]:
                score += 0.3
                reasons.append("failure pattern matches retry logic")
            
            # Success rate bonus
            score *= playbook["success_rate"]
            
            if score > 0.1:
                recommendations.append(Recommendation(
                    playbook_id=playbook["id"],
                    score=min(1.0, score),
                    justification=f"Recommended because: {', '.join(reasons)}",
                    confidence=min(0.8, score),
                    metadata={
                        "success_rate": playbook["success_rate"],
                        "avg_duration": playbook["avg_duration"],
                        "safety_mode": playbook["safety_mode"]
                    }
                ))
        
        # Sort by score and limit
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]
    
    def _calculate_similarity_score(self, query_text: str, playbook: Dict[str, Any]) -> float:
        """Calculate similarity score between query and playbook."""
        # Simple keyword-based similarity
        query_words = set(query_text.lower().split())
        playbook_words = set((playbook["name"] + " " + playbook["description"]).lower().split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words & playbook_words
        union = query_words | playbook_words
        
        jaccard_similarity = len(intersection) / len(union) if union else 0.0
        
        # Boost score based on tag matches
        tag_matches = sum(1 for tag in playbook["tags"] if tag in query_text.lower())
        tag_boost = tag_matches * 0.2
        
        return min(1.0, jaccard_similarity + tag_boost)
    
    def _generate_justification(self, playbook: Dict[str, Any], context: Dict[str, Any], score: float) -> str:
        """Generate human-readable justification for recommendation."""
        reasons = []
        
        if score > 0.7:
            reasons.append("high similarity to historical incidents")
        elif score > 0.4:
            reasons.append("moderate similarity to known patterns")
        
        if playbook["success_rate"] > 0.9:
            reasons.append("high success rate")
        
        if context["labels"]:
            reasons.append("matches incident labels")
        
        return f"Recommended because: {', '.join(reasons)}"

# Global engine instance
engine = RecommenderEngine()

@app.post("/recommend", response_model=RecommendResponse)
async def recommend_endpoint(request: RecommendRequest):
    """Generate playbook recommendations for incident."""
    return engine.recommend(request)

@app.get("/playbooks")
async def get_playbooks():
    """Get available playbooks."""
    return {"playbooks": engine.playbooks}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "playbooks_loaded": len(engine.playbooks),
        "vectors_loaded": bool(engine.vectors),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import Response
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)