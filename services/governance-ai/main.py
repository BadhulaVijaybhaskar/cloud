#!/usr/bin/env python3
"""
Governance AI Service - E.4
Automated security and policy checks for marketplace submissions
"""
import os
import json
import time
import uuid
import re
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Dict, List, Optional
import sqlite3

app = FastAPI(title="Governance AI", version="1.0.0")
security = HTTPBearer()

# Environment
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
DB_PATH = os.getenv("GOVERNANCE_DB", "/tmp/governance.db")

class AnalysisRequest(BaseModel):
    id: str
    content: Dict
    metadata: Optional[Dict] = {}

class PolicyViolation(BaseModel):
    rule: str
    severity: str
    description: str
    line: Optional[int] = None

class AnalysisResult(BaseModel):
    id: str
    risk_score: float
    violations: List[PolicyViolation]
    recommendations: List[str]
    approved: bool

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            content_id TEXT NOT NULL,
            risk_score REAL NOT NULL,
            violations_count INTEGER NOT NULL,
            approved INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

class GovernanceAnalyzer:
    """AI-powered governance and policy analyzer"""
    
    def __init__(self):
        self.security_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'HIGH', 'Hardcoded password detected'),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'HIGH', 'Hardcoded API key detected'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'MEDIUM', 'Hardcoded secret detected'),
            (r'eval\s*\(', 'HIGH', 'Dangerous eval() function usage'),
            (r'exec\s*\(', 'HIGH', 'Dangerous exec() function usage'),
            (r'subprocess\.call', 'MEDIUM', 'System command execution'),
            (r'os\.system', 'HIGH', 'Direct system command execution'),
        ]
        
        self.policy_rules = [
            ('P-1', 'Data Privacy', self._check_data_privacy),
            ('P-2', 'Secrets & Signing', self._check_secrets),
            ('P-3', 'Execution Safety', self._check_execution_safety),
            ('P-4', 'Observability', self._check_observability),
            ('P-5', 'Multi-Tenancy', self._check_multi_tenancy),
            ('P-6', 'Performance Budget', self._check_performance),
        ]
    
    def analyze(self, content: Dict) -> AnalysisResult:
        """Perform comprehensive governance analysis"""
        violations = []
        
        # Convert content to string for pattern matching
        content_str = json.dumps(content, indent=2)
        
        # Security pattern analysis
        for pattern, severity, description in self.security_patterns:
            matches = re.finditer(pattern, content_str, re.IGNORECASE)
            for match in matches:
                line_num = content_str[:match.start()].count('\n') + 1
                violations.append(PolicyViolation(
                    rule=f"SEC-{severity}",
                    severity=severity,
                    description=description,
                    line=line_num
                ))
        
        # Policy compliance checks
        for rule_id, rule_name, check_func in self.policy_rules:
            policy_violations = check_func(content)
            violations.extend(policy_violations)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(violations)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(violations)
        
        # Approval decision
        approved = risk_score < 0.3 and not any(v.severity == 'HIGH' for v in violations)
        
        return AnalysisResult(
            id=str(uuid.uuid4()),
            risk_score=risk_score,
            violations=violations,
            recommendations=recommendations,
            approved=approved
        )
    
    def _check_data_privacy(self, content: Dict) -> List[PolicyViolation]:
        """Check P-1 Data Privacy compliance"""
        violations = []
        content_str = json.dumps(content).lower()
        
        pii_patterns = ['email', 'phone', 'ssn', 'credit_card', 'address']
        for pattern in pii_patterns:
            if pattern in content_str:
                violations.append(PolicyViolation(
                    rule="P-1",
                    severity="MEDIUM",
                    description=f"Potential PII detected: {pattern}"
                ))
        
        return violations
    
    def _check_secrets(self, content: Dict) -> List[PolicyViolation]:
        """Check P-2 Secrets & Signing compliance"""
        violations = []
        content_str = json.dumps(content)
        
        if 'signature' not in content_str:
            violations.append(PolicyViolation(
                rule="P-2",
                severity="HIGH",
                description="Missing required signature"
            ))
        
        return violations
    
    def _check_execution_safety(self, content: Dict) -> List[PolicyViolation]:
        """Check P-3 Execution Safety compliance"""
        violations = []
        
        if content.get('auto_execute', False) and not content.get('dry_run_passed', False):
            violations.append(PolicyViolation(
                rule="P-3",
                severity="HIGH",
                description="Auto-execution without dry run validation"
            ))
        
        return violations
    
    def _check_observability(self, content: Dict) -> List[PolicyViolation]:
        """Check P-4 Observability compliance"""
        violations = []
        
        required_endpoints = ['/health', '/metrics']
        for endpoint in required_endpoints:
            if endpoint not in json.dumps(content):
                violations.append(PolicyViolation(
                    rule="P-4",
                    severity="LOW",
                    description=f"Missing {endpoint} endpoint"
                ))
        
        return violations
    
    def _check_multi_tenancy(self, content: Dict) -> List[PolicyViolation]:
        """Check P-5 Multi-Tenancy compliance"""
        violations = []
        content_str = json.dumps(content)
        
        if 'tenant' not in content_str and 'jwt' not in content_str:
            violations.append(PolicyViolation(
                rule="P-5",
                severity="MEDIUM",
                description="No tenant isolation mechanism detected"
            ))
        
        return violations
    
    def _check_performance(self, content: Dict) -> List[PolicyViolation]:
        """Check P-6 Performance Budget compliance"""
        violations = []
        
        # Check for potential performance issues
        content_str = json.dumps(content).lower()
        performance_risks = ['while true', 'infinite loop', 'recursive']
        
        for risk in performance_risks:
            if risk in content_str:
                violations.append(PolicyViolation(
                    rule="P-6",
                    severity="MEDIUM",
                    description=f"Performance risk detected: {risk}"
                ))
        
        return violations
    
    def _calculate_risk_score(self, violations: List[PolicyViolation]) -> float:
        """Calculate overall risk score (0.0 - 1.0)"""
        if not violations:
            return 0.0
        
        severity_weights = {'LOW': 0.1, 'MEDIUM': 0.3, 'HIGH': 0.7}
        total_weight = sum(severity_weights.get(v.severity, 0.1) for v in violations)
        
        # Normalize to 0-1 scale
        max_possible = len(violations) * 0.7  # Assume all HIGH
        return min(total_weight / max_possible, 1.0) if max_possible > 0 else 0.0
    
    def _generate_recommendations(self, violations: List[PolicyViolation]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if any(v.rule.startswith('SEC-') for v in violations):
            recommendations.append("Remove hardcoded secrets and use environment variables")
        
        if any(v.rule == 'P-2' for v in violations):
            recommendations.append("Add proper cryptographic signatures using cosign")
        
        if any(v.rule == 'P-3' for v in violations):
            recommendations.append("Implement dry-run validation before auto-execution")
        
        if any(v.rule == 'P-4' for v in violations):
            recommendations.append("Add /health and /metrics endpoints for observability")
        
        if any(v.rule == 'P-5' for v in violations):
            recommendations.append("Implement JWT-based tenant isolation")
        
        return recommendations

# Global analyzer instance
analyzer = GovernanceAnalyzer()

@app.on_event("startup")
async def startup():
    init_db()
    print(f"Governance AI started (SIMULATION_MODE={SIMULATION_MODE})")

@app.post("/analyze")
async def analyze_content(request: AnalysisRequest, token: str = Depends(security)):
    """Analyze content for security and policy compliance"""
    
    result = analyzer.analyze(request.content)
    
    # Store analysis result
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO analyses (id, content_id, risk_score, violations_count, approved, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (result.id, request.id, result.risk_score, len(result.violations), 
          int(result.approved), int(time.time())))
    conn.commit()
    conn.close()
    
    return result

@app.get("/models")
async def list_models():
    """List available governance models"""
    return {
        "models": [
            {
                "id": "security-scanner-v1",
                "name": "Security Pattern Scanner",
                "version": "1.0.0",
                "description": "Detects hardcoded secrets and dangerous functions"
            },
            {
                "id": "policy-checker-v1", 
                "name": "Policy Compliance Checker",
                "version": "1.0.0",
                "description": "Validates against P-1 through P-6 policies"
            }
        ],
        "active_model": "combined-v1",
        "simulation_mode": SIMULATION_MODE
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "governance-ai",
        "simulation_mode": SIMULATION_MODE,
        "models_loaded": 2
    }

@app.get("/metrics")
async def metrics():
    conn = sqlite3.connect(DB_PATH)
    
    cursor = conn.execute("SELECT COUNT(*) FROM analyses")
    total_analyses = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(*) FROM analyses WHERE approved = 1")
    approved_count = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT AVG(risk_score) FROM analyses")
    avg_risk_score = cursor.fetchone()[0] or 0.0
    
    conn.close()
    
    return {
        "governance_analyses_total": total_analyses,
        "governance_approved_count": approved_count,
        "governance_avg_risk_score": round(avg_risk_score, 3)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8070)