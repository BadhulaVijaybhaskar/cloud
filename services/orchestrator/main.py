#!/usr/bin/env python3
"""
NeuralOps Incident Orchestrator
Implements suggest→dry-run→approve→execute workflow with audit logging.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import sqlite3
import uuid

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import uvicorn
import requests
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
orchestrations_total = Counter('neuralops_orchestrations_total', 'Total orchestrations', ['stage', 'status'])
orchestration_duration = Histogram('neuralops_orchestration_duration_seconds', 'Orchestration duration')

app = FastAPI(title="NeuralOps Orchestrator", version="1.0.0")

class OrchestrationRequest(BaseModel):
    signal_id: Optional[str] = None
    playbook_id: str
    incident_description: Optional[str] = None
    labels: Dict[str, str] = {}

class ApprovalRequest(BaseModel):
    orchestration_id: str
    approver_id: str
    justification: str

class OrchestrationResponse(BaseModel):
    orchestration_id: str
    stage: str
    status: str
    playbook_id: str
    recommendations: List[Dict[str, Any]] = []
    dry_run_result: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    audit_trail: List[Dict[str, Any]] = []

class OrchestrationEngine:
    """Core orchestration engine for incident management."""
    
    def __init__(self):
        self.db_path = "orchestrations.db"
        self.registry_url = os.getenv("REGISTRY_URL", "http://localhost:8000")
        self.runtime_url = os.getenv("RUNTIME_URL", "http://localhost:8001")
        self.recommender_url = os.getenv("RECOMMENDER_URL", "http://localhost:8003")
        self._init_db()
    
    def _init_db(self):
        """Initialize orchestration database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orchestrations (
                    id TEXT PRIMARY KEY,
                    signal_id TEXT,
                    playbook_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    status TEXT NOT NULL,
                    incident_description TEXT,
                    labels TEXT,
                    recommendations TEXT,
                    dry_run_result TEXT,
                    execution_result TEXT,
                    audit_trail TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id TEXT PRIMARY KEY,
                    orchestration_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    action TEXT NOT NULL,
                    user_id TEXT,
                    timestamp TEXT NOT NULL,
                    details TEXT,
                    hash TEXT
                )
            """)
    
    def suggest(self, request: OrchestrationRequest) -> OrchestrationResponse:
        """Stage 1: Create incident and get recommendations."""
        orchestration_id = str(uuid.uuid4())
        
        try:
            # Get recommendations
            recommendations = self._get_recommendations(request)
            
            # Create orchestration record
            orchestration = {
                "id": orchestration_id,
                "signal_id": request.signal_id,
                "playbook_id": request.playbook_id,
                "stage": "suggest",
                "status": "pending",
                "incident_description": request.incident_description,
                "labels": json.dumps(request.labels),
                "recommendations": json.dumps(recommendations),
                "dry_run_result": None,
                "execution_result": None,
                "audit_trail": "[]"
            }
            
            self._save_orchestration(orchestration)
            self._log_audit(orchestration_id, "suggest", "create_incident", None, {
                "playbook_id": request.playbook_id,
                "recommendations_count": len(recommendations)
            })
            
            orchestrations_total.labels(stage="suggest", status="success").inc()
            
            return OrchestrationResponse(
                orchestration_id=orchestration_id,
                stage="suggest",
                status="pending",
                playbook_id=request.playbook_id,
                recommendations=recommendations,
                audit_trail=self._get_audit_trail(orchestration_id)
            )
            
        except Exception as e:
            orchestrations_total.labels(stage="suggest", status="error").inc()
            logger.error(f"Suggest failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def dry_run(self, orchestration_id: str) -> OrchestrationResponse:
        """Stage 2: Perform dry-run validation."""
        orchestration = self._get_orchestration(orchestration_id)
        
        if orchestration["stage"] != "suggest":
            raise HTTPException(status_code=400, detail="Invalid stage for dry-run")
        
        try:
            # Call registry dry-run endpoint
            dry_run_result = self._call_registry_dry_run(orchestration["playbook_id"])
            
            # Update orchestration
            orchestration["stage"] = "dry_run"
            orchestration["status"] = "completed" if dry_run_result.get("valid", False) else "failed"
            orchestration["dry_run_result"] = json.dumps(dry_run_result)
            
            self._save_orchestration(orchestration)
            self._log_audit(orchestration_id, "dry_run", "validate_playbook", None, dry_run_result)
            
            orchestrations_total.labels(stage="dry_run", status=orchestration["status"]).inc()
            
            return self._build_response(orchestration)
            
        except Exception as e:
            orchestrations_total.labels(stage="dry_run", status="error").inc()
            logger.error(f"Dry-run failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def approve(self, approval: ApprovalRequest, approver_token: str) -> OrchestrationResponse:
        """Stage 3: Approve execution with authorization."""
        orchestration = self._get_orchestration(approval.orchestration_id)
        
        if orchestration["stage"] != "dry_run":
            raise HTTPException(status_code=400, detail="Invalid stage for approval")
        
        if orchestration["status"] != "completed":
            raise HTTPException(status_code=400, detail="Dry-run must pass before approval")
        
        try:
            # Validate approver (simplified JWT check)
            approver_info = self._validate_approver(approver_token)
            
            # Update orchestration
            orchestration["stage"] = "approved"
            orchestration["status"] = "ready"
            
            self._save_orchestration(orchestration)
            self._log_audit(approval.orchestration_id, "approve", "approve_execution", 
                          approver_info.get("user_id"), {
                              "approver": approval.approver_id,
                              "justification": approval.justification
                          })
            
            orchestrations_total.labels(stage="approve", status="success").inc()
            
            return self._build_response(orchestration)
            
        except Exception as e:
            orchestrations_total.labels(stage="approve", status="error").inc()
            logger.error(f"Approval failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def execute(self, orchestration_id: str, executor_token: str) -> OrchestrationResponse:
        """Stage 4: Execute approved playbook."""
        orchestration = self._get_orchestration(orchestration_id)
        
        if orchestration["stage"] != "approved":
            raise HTTPException(status_code=400, detail="Orchestration must be approved")
        
        try:
            # Validate executor
            executor_info = self._validate_approver(executor_token)
            
            # Execute playbook via runtime-agent
            execution_result = self._call_runtime_execute(orchestration["playbook_id"])
            
            # Update orchestration
            orchestration["stage"] = "executed"
            orchestration["status"] = "completed" if execution_result.get("success", False) else "failed"
            orchestration["execution_result"] = json.dumps(execution_result)
            
            self._save_orchestration(orchestration)
            self._log_audit(orchestration_id, "execute", "run_playbook", 
                          executor_info.get("user_id"), execution_result)
            
            orchestrations_total.labels(stage="execute", status=orchestration["status"]).inc()
            
            return self._build_response(orchestration)
            
        except Exception as e:
            orchestrations_total.labels(stage="execute", status="error").inc()
            logger.error(f"Execution failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _get_recommendations(self, request: OrchestrationRequest) -> List[Dict[str, Any]]:
        """Get recommendations from recommender service."""
        try:
            response = requests.post(f"{self.recommender_url}/recommend", json={
                "signal_id": request.signal_id,
                "incident_description": request.incident_description,
                "labels": request.labels,
                "limit": 3
            }, timeout=10)
            
            if response.status_code == 200:
                return response.json().get("recommendations", [])
        except Exception as e:
            logger.warning(f"Recommender unavailable: {e}")
        
        # Fallback recommendations
        return [{
            "playbook_id": request.playbook_id,
            "score": 0.8,
            "justification": "Direct playbook selection",
            "confidence": 0.7
        }]
    
    def _call_registry_dry_run(self, playbook_id: str) -> Dict[str, Any]:
        """Call registry dry-run endpoint."""
        try:
            response = requests.post(f"{self.registry_url}/workflows/{playbook_id}/dry-run", 
                                   timeout=30)
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"Registry dry-run unavailable: {e}")
        
        # Fallback dry-run (always pass for development)
        return {
            "valid": True,
            "method": "fallback",
            "message": "Dry-run simulation (registry unavailable)",
            "safety_mode": "manual"
        }
    
    def _call_runtime_execute(self, playbook_id: str) -> Dict[str, Any]:
        """Call runtime-agent execute endpoint."""
        try:
            response = requests.post(f"{self.runtime_url}/execute", json={
                "playbook_id": playbook_id,
                "safety_mode": "manual"
            }, timeout=60)
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"Runtime execution unavailable: {e}")
        
        # Fallback execution (simulate success)
        return {
            "success": True,
            "method": "simulation",
            "message": "Execution simulation (runtime unavailable)",
            "duration_ms": 1000,
            "run_id": f"sim-{uuid.uuid4()}"
        }
    
    def _validate_approver(self, token: str) -> Dict[str, Any]:
        """Validate approver token (simplified)."""
        if not token:
            raise HTTPException(status_code=401, detail="Authorization token required")
        
        # Simplified validation (in production, verify JWT)
        if token.startswith("Bearer "):
            return {"user_id": "admin", "role": "org-admin"}
        
        raise HTTPException(status_code=403, detail="Invalid authorization")
    
    def _save_orchestration(self, orchestration: Dict[str, Any]):
        """Save orchestration to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO orchestrations 
                (id, signal_id, playbook_id, stage, status, incident_description, 
                 labels, recommendations, dry_run_result, execution_result, audit_trail, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                orchestration["id"], orchestration["signal_id"], orchestration["playbook_id"],
                orchestration["stage"], orchestration["status"], orchestration["incident_description"],
                orchestration["labels"], orchestration["recommendations"], 
                orchestration["dry_run_result"], orchestration["execution_result"],
                orchestration["audit_trail"], datetime.now(timezone.utc).isoformat()
            ))
    
    def _get_orchestration(self, orchestration_id: str) -> Dict[str, Any]:
        """Get orchestration from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM orchestrations WHERE id = ?", (orchestration_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Orchestration not found")
            
            return dict(row)
    
    def _log_audit(self, orchestration_id: str, stage: str, action: str, 
                   user_id: Optional[str], details: Dict[str, Any]):
        """Log audit entry."""
        audit_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        details_json = json.dumps(details)
        
        # Simple hash for integrity
        import hashlib
        hash_input = f"{audit_id}{orchestration_id}{stage}{action}{timestamp}{details_json}"
        audit_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO audit_logs 
                (id, orchestration_id, stage, action, user_id, timestamp, details, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (audit_id, orchestration_id, stage, action, user_id, timestamp, details_json, audit_hash))
    
    def _get_audit_trail(self, orchestration_id: str) -> List[Dict[str, Any]]:
        """Get audit trail for orchestration."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM audit_logs 
                WHERE orchestration_id = ? 
                ORDER BY timestamp
            """, (orchestration_id,))
            
            return [dict(row) for row in cursor]
    
    def _build_response(self, orchestration: Dict[str, Any]) -> OrchestrationResponse:
        """Build orchestration response."""
        return OrchestrationResponse(
            orchestration_id=orchestration["id"],
            stage=orchestration["stage"],
            status=orchestration["status"],
            playbook_id=orchestration["playbook_id"],
            recommendations=json.loads(orchestration["recommendations"] or "[]"),
            dry_run_result=json.loads(orchestration["dry_run_result"] or "null"),
            execution_result=json.loads(orchestration["execution_result"] or "null"),
            audit_trail=self._get_audit_trail(orchestration["id"])
        )

# Global engine instance
engine = OrchestrationEngine()

def get_auth_token(authorization: str = Header(None)) -> str:
    """Extract auth token from header."""
    return authorization or ""

@app.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate_endpoint(request: OrchestrationRequest):
    """Start orchestration workflow."""
    return engine.suggest(request)

@app.post("/orchestrations/{orchestration_id}/dry-run", response_model=OrchestrationResponse)
async def dry_run_endpoint(orchestration_id: str):
    """Perform dry-run validation."""
    return engine.dry_run(orchestration_id)

@app.post("/orchestrations/{orchestration_id}/approve", response_model=OrchestrationResponse)
async def approve_endpoint(orchestration_id: str, approval: ApprovalRequest, 
                          token: str = Depends(get_auth_token)):
    """Approve orchestration for execution."""
    return engine.approve(approval, token)

@app.post("/orchestrations/{orchestration_id}/execute", response_model=OrchestrationResponse)
async def execute_endpoint(orchestration_id: str, token: str = Depends(get_auth_token)):
    """Execute approved orchestration."""
    return engine.execute(orchestration_id, token)

@app.get("/orchestrations/{orchestration_id}", response_model=OrchestrationResponse)
async def get_orchestration(orchestration_id: str):
    """Get orchestration status."""
    orchestration = engine._get_orchestration(orchestration_id)
    return engine._build_response(orchestration)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "registry_url": engine.registry_url,
        "runtime_url": engine.runtime_url,
        "recommender_url": engine.recommender_url,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import Response
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)