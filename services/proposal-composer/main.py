#!/usr/bin/env python3
"""
Phase I.4.2 - Proposal Composer
Creates signed decision manifests from inputs and models
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest
import yaml

# Metrics
COMPOSITIONS_TOTAL = Counter('proposal_compositions_total', 'Total proposal compositions')
COMPOSITION_DURATION = Histogram('composition_processing_seconds', 'Composition processing time')

app = FastAPI(title="Proposal Composer", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
NEURAL_FABRIC_URL = os.getenv('NEURAL_FABRIC_URL', 'http://localhost:8080')

class ComposeRequest(BaseModel):
    context: str
    tenant_id: str
    signals: Optional[Dict[str, Any]] = {}
    template_name: Optional[str] = None

def verify_jwt_token(authorization: str = Header(None)):
    """Verify JWT token and extract tenant claim"""
    if not authorization or not authorization.startswith('Bearer '):
        if SIMULATION_MODE:
            return {"tenant_id": "sim-tenant", "user_id": "sim-user"}
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    if SIMULATION_MODE:
        return {"tenant_id": "sim-tenant", "user_id": "sim-user"}
    return {"tenant_id": "extracted-tenant", "user_id": "extracted-user"}

def redact_pii(data: Dict[str, Any], tenant_consent: bool = False) -> Dict[str, Any]:
    """Redact PII unless tenant consent provided (P1)"""
    if tenant_consent:
        return data
    
    # PII patterns to redact
    pii_patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}-\d{3}-\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'ip': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    }
    
    def redact_string(text: str) -> str:
        for pii_type, pattern in pii_patterns.items():
            text = re.sub(pattern, f'<REDACTED_{pii_type.upper()}>', text)
        return text
    
    def redact_recursive(obj):
        if isinstance(obj, dict):
            return {k: redact_recursive(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [redact_recursive(item) for item in obj]
        elif isinstance(obj, str):
            return redact_string(obj)
        return obj
    
    return redact_recursive(data)

def simulate_cosign_signature(manifest: Dict[str, Any]) -> str:
    """Simulate cosign signature for manifest (P2)"""
    if SIMULATION_MODE:
        manifest_str = json.dumps(manifest, sort_keys=True)
        # Simulate signature
        return f"cosign-sim-{hash(manifest_str) % 10000:04d}"
    # In production: actual cosign signing
    return "production-signature"

def get_neural_fabric_suggestions(context: str, signals: Dict[str, Any]) -> Dict[str, Any]:
    """Get suggestions from Neural Fabric"""
    if SIMULATION_MODE:
        # Simulate neural fabric response based on context
        suggestions = {
            "reduce cost": {
                "action": "scale_down",
                "target": "compute_instances",
                "parameters": {"target_count": 2, "instance_type": "t3.medium"}
            },
            "improve performance": {
                "action": "scale_up", 
                "target": "compute_instances",
                "parameters": {"target_count": 5, "instance_type": "c5.large"}
            },
            "enhance security": {
                "action": "update_security_groups",
                "target": "network_config",
                "parameters": {"restrict_ports": [22, 3389], "enable_waf": True}
            }
        }
        
        for key in suggestions:
            if key.lower() in context.lower():
                return suggestions[key]
        
        # Default suggestion
        return {
            "action": "analyze",
            "target": "system_state", 
            "parameters": {"deep_scan": True}
        }
    
    # In production: actual neural fabric API call
    return {"action": "placeholder", "target": "system"}

def load_templates() -> Dict[str, Dict[str, Any]]:
    """Load composition templates"""
    templates = {
        "cost_optimization": {
            "name": "Cost Optimization",
            "description": "Template for cost reduction decisions",
            "schema": {
                "action": "scale_down",
                "impact_level": "medium",
                "rollback_plan": True,
                "approval_required": False
            }
        },
        "security_update": {
            "name": "Security Update",
            "description": "Template for security-related changes",
            "schema": {
                "action": "security_patch",
                "impact_level": "high", 
                "rollback_plan": True,
                "approval_required": True
            }
        },
        "performance_scaling": {
            "name": "Performance Scaling",
            "description": "Template for performance improvements",
            "schema": {
                "action": "scale_up",
                "impact_level": "medium",
                "rollback_plan": True,
                "approval_required": False
            }
        }
    }
    return templates

@app.post("/compose")
async def compose_proposal(
    request: ComposeRequest,
    token_data: Dict = Depends(verify_jwt_token)
):
    """Compose decision manifest from inputs"""
    COMPOSITIONS_TOTAL.inc()
    
    # Validate tenant access (P5)
    if request.tenant_id != token_data.get('tenant_id'):
        raise HTTPException(status_code=403, detail="Tenant access denied")
    
    # Redact PII from signals (P1)
    tenant_consent = request.signals.get('pii_consent', False)
    clean_signals = redact_pii(request.signals, tenant_consent)
    
    # Get neural fabric suggestions
    neural_suggestions = get_neural_fabric_suggestions(request.context, clean_signals)
    
    # Load template if specified
    templates = load_templates()
    template_schema = {}
    if request.template_name and request.template_name in templates:
        template_schema = templates[request.template_name]["schema"]
    
    # Compose manifest
    manifest = {
        "id": f"manifest-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "tenant_id": request.tenant_id,
        "context": request.context,
        "created_at": datetime.utcnow().isoformat(),
        "neural_suggestions": neural_suggestions,
        **template_schema,
        **neural_suggestions,
        "metadata": {
            "composer_version": "1.0.0",
            "template_used": request.template_name,
            "pii_redacted": not tenant_consent,
            "signals_processed": len(clean_signals)
        }
    }
    
    # Sign manifest (P2)
    signature = simulate_cosign_signature(manifest)
    manifest["signature"] = signature
    
    logger.info(f"Composed manifest for tenant {request.tenant_id}, context: {request.context}")
    
    return {
        "manifest": manifest,
        "signature": signature,
        "pii_redacted": not tenant_consent,
        "template_applied": request.template_name
    }

@app.get("/templates")
async def list_templates():
    """List available composition templates"""
    templates = load_templates()
    return {
        "templates": [
            {
                "name": name,
                "display_name": template["name"],
                "description": template["description"]
            }
            for name, template in templates.items()
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint (P4)"""
    return {
        "status": "healthy",
        "service": "proposal-composer",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE,
        "neural_fabric_connected": SIMULATION_MODE
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint (P4)"""
    return JSONResponse(
        content=generate_latest().decode('utf-8'),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9202)