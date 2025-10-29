from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

app = FastAPI(title="Policy-Aware Context Auditor", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

class AuditRequest(BaseModel):
    entity_id: str
    context_data: Dict[str, Any]
    operation: str  # "read", "write", "fusion", "routing"
    tenant_id: str

class PolicyViolation(BaseModel):
    policy_id: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    remediation: str

class AuditResult(BaseModel):
    entity_id: str
    compliance_status: str  # "compliant", "violations", "critical"
    violations: List[PolicyViolation]
    bias_score: float
    audit_hash: str
    tenant_id: str

# Policy definitions (P1-P7)
POLICIES = {
    "P1": {"name": "Data Privacy", "threshold": 0.8},
    "P2": {"name": "Secrets & Signing", "threshold": 1.0},
    "P3": {"name": "Execution Safety", "threshold": 0.9},
    "P4": {"name": "Observability", "threshold": 0.7},
    "P5": {"name": "Multi-Tenancy", "threshold": 1.0},
    "P6": {"name": "Performance Budget", "threshold": 0.8},
    "P7": {"name": "Resilience & Recovery", "threshold": 0.8}
}

# Audit log
audit_log = {}
violation_stats = {}

@app.get("/health")
async def health():
    return {"status": "healthy", "simulation_mode": SIMULATION_MODE}

@app.get("/metrics")
async def metrics():
    return {
        "audits_performed": len(audit_log),
        "total_violations": sum(len(v.get("violations", [])) for v in audit_log.values()),
        "simulation_mode": SIMULATION_MODE,
        "compliance_rate": 0.94  # Mock compliance rate
    }

@app.post("/audit/context")
async def audit_context_operation(request: AuditRequest):
    """Evaluate compliance with P1-P7 policies"""
    try:
        violations = []
        
        # P1: Data Privacy - Check for PII exposure
        if _contains_pii(request.context_data):
            violations.append(PolicyViolation(
                policy_id="P1",
                severity="high",
                description="Context contains potential PII without anonymization",
                remediation="Apply data anonymization before storage"
            ))
        
        # P2: Secrets & Signing - Check for exposed secrets
        if _contains_secrets(request.context_data):
            violations.append(PolicyViolation(
                policy_id="P2",
                severity="critical",
                description="Context contains exposed secrets or credentials",
                remediation="Remove secrets and use secure vault references"
            ))
        
        # P3: Execution Safety - Check for high-risk operations
        if request.operation in ["fusion", "routing"] and _is_high_risk_context(request.context_data):
            violations.append(PolicyViolation(
                policy_id="P3",
                severity="medium",
                description="High-risk context operation requires approval",
                remediation="Route through approval workflow"
            ))
        
        # P5: Multi-Tenancy - Validate tenant isolation
        if not _validate_tenant_isolation(request.tenant_id, request.context_data):
            violations.append(PolicyViolation(
                policy_id="P5",
                severity="critical",
                description="Cross-tenant data leakage detected",
                remediation="Enforce strict tenant boundaries"
            ))
        
        # Calculate bias score (mock implementation)
        bias_score = _calculate_bias_score(request.context_data)
        
        if bias_score > 0.7:
            violations.append(PolicyViolation(
                policy_id="P1",
                severity="medium",
                description=f"High bias score detected: {bias_score:.2f}",
                remediation="Review context for algorithmic bias"
            ))
        
        # Determine compliance status
        if any(v.severity == "critical" for v in violations):
            compliance_status = "critical"
        elif violations:
            compliance_status = "violations"
        else:
            compliance_status = "compliant"
        
        # Generate audit hash
        audit_data = {
            "entity_id": request.entity_id,
            "tenant_id": request.tenant_id,
            "operation": request.operation,
            "violations_count": len(violations),
            "timestamp": datetime.utcnow().isoformat()
        }
        audit_hash = hashlib.sha256(json.dumps(audit_data, sort_keys=True).encode()).hexdigest()[:16]
        
        result = AuditResult(
            entity_id=request.entity_id,
            compliance_status=compliance_status,
            violations=violations,
            bias_score=bias_score,
            audit_hash=audit_hash,
            tenant_id=request.tenant_id
        )
        
        # Log audit result
        audit_key = f"{request.tenant_id}:{request.entity_id}:{request.operation}"
        audit_log[audit_key] = {
            "result": result.dict(),
            "timestamp": datetime.utcnow().isoformat(),
            "context_hash": hashlib.sha256(json.dumps(request.context_data, sort_keys=True).encode()).hexdigest()[:16]
        }
        
        # Update violation statistics
        for violation in violations:
            policy_id = violation.policy_id
            if policy_id not in violation_stats:
                violation_stats[policy_id] = {"count": 0, "severity_breakdown": {}}
            
            violation_stats[policy_id]["count"] += 1
            severity = violation.severity
            if severity not in violation_stats[policy_id]["severity_breakdown"]:
                violation_stats[policy_id]["severity_breakdown"][severity] = 0
            violation_stats[policy_id]["severity_breakdown"][severity] += 1
        
        logger.info(f"Audited {request.operation} for {request.entity_id}: {compliance_status}")
        
        return result
        
    except Exception as e:
        logger.error(f"Audit error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _contains_pii(context_data: Dict[str, Any]) -> bool:
    """Check if context contains PII"""
    pii_indicators = ["email", "phone", "ssn", "address", "name", "credit_card"]
    context_str = json.dumps(context_data).lower()
    
    for indicator in pii_indicators:
        if indicator in context_str:
            return True
    return False

def _contains_secrets(context_data: Dict[str, Any]) -> bool:
    """Check if context contains secrets"""
    secret_indicators = ["password", "token", "key", "secret", "credential"]
    context_str = json.dumps(context_data).lower()
    
    for indicator in secret_indicators:
        if indicator in context_str:
            return True
    return False

def _is_high_risk_context(context_data: Dict[str, Any]) -> bool:
    """Determine if context operation is high-risk"""
    risk_indicators = ["admin", "root", "delete", "drop", "truncate"]
    context_str = json.dumps(context_data).lower()
    
    for indicator in risk_indicators:
        if indicator in context_str:
            return True
    return False

def _validate_tenant_isolation(tenant_id: str, context_data: Dict[str, Any]) -> bool:
    """Validate tenant isolation"""
    # Mock validation - check if context references other tenants
    context_str = json.dumps(context_data).lower()
    
    # Simple check for other tenant references
    if "tenant" in context_str and tenant_id.lower() not in context_str:
        return False
    
    return True

def _calculate_bias_score(context_data: Dict[str, Any]) -> float:
    """Calculate algorithmic bias score"""
    # Mock bias calculation
    bias_indicators = ["gender", "race", "age", "religion", "nationality"]
    context_str = json.dumps(context_data).lower()
    
    bias_count = sum(1 for indicator in bias_indicators if indicator in context_str)
    return min(bias_count * 0.2, 1.0)

@app.get("/audit/violations/{entity_id}")
async def get_violations(entity_id: str, tenant_id: str):
    """Get violation history for entity"""
    entity_violations = []
    
    for key, audit_entry in audit_log.items():
        if key.startswith(f"{tenant_id}:{entity_id}:"):
            entity_violations.append({
                "operation": key.split(":")[-1],
                "violations": audit_entry["result"]["violations"],
                "compliance_status": audit_entry["result"]["compliance_status"],
                "timestamp": audit_entry["timestamp"]
            })
    
    return {
        "entity_id": entity_id,
        "tenant_id": tenant_id,
        "violations": entity_violations,
        "total_audits": len(entity_violations)
    }

@app.get("/audit/compliance-report")
async def get_compliance_report(tenant_id: str):
    """Generate compliance report for tenant"""
    tenant_audits = [
        audit for key, audit in audit_log.items()
        if key.startswith(f"{tenant_id}:")
    ]
    
    total_audits = len(tenant_audits)
    compliant_audits = sum(1 for audit in tenant_audits 
                          if audit["result"]["compliance_status"] == "compliant")
    
    compliance_rate = compliant_audits / total_audits if total_audits > 0 else 1.0
    
    return {
        "tenant_id": tenant_id,
        "total_audits": total_audits,
        "compliant_audits": compliant_audits,
        "compliance_rate": compliance_rate,
        "violation_stats": violation_stats,
        "report_timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9106)