"""
Policy engine for WPK workflow evaluation and approval decisions.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

from .static_validator import ValidationResult, ValidationIssue, Severity

logger = logging.getLogger(__name__)

class PolicyDecision(Enum):
    APPROVE = "approve"
    REVIEW = "review"
    BLOCK = "block"

class SafetyMode(Enum):
    AUTO = "auto"
    MANUAL = "manual"

@dataclass
class PolicyResult:
    """Result of policy evaluation."""
    valid: bool
    policy_decision: PolicyDecision
    approval_required: bool
    risk_score: int
    errors: List[str]
    warnings: List[str]
    
    @property
    def can_execute(self) -> bool:
        return self.policy_decision == PolicyDecision.APPROVE and not self.approval_required

@dataclass
class ApprovalRequest:
    """Approval request for high-risk workflows."""
    workflow_id: str
    risk_score: int
    issues: List[ValidationIssue]
    justification: str
    requested_by: str
    requested_at: datetime
    expires_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "risk_score": self.risk_score,
            "issues": [
                {
                    "rule_id": issue.rule_id,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "path": issue.path,
                    "suggestion": issue.suggestion,
                    "cwe": issue.cwe
                }
                for issue in self.issues
            ],
            "justification": self.justification,
            "requested_by": self.requested_by,
            "requested_at": self.requested_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }

class PolicyEngine:
    """Policy engine for workflow approval decisions."""
    
    def __init__(self):
        self.policies = self._load_policies()
    
    def _load_policies(self) -> Dict[str, Dict]:
        """Load policy configuration."""
        return {
            "risk_thresholds": {
                "low": 25,
                "medium": 50,
                "high": 75,
                "critical": 100
            },
            "auto_approve_threshold": 25,
            "review_threshold": 50,
            "block_threshold": 75,
            "approval_expiry_hours": 24,
            "max_approval_duration_days": 30
        }
    
    def evaluate(self, validation_result: ValidationResult, wpk_data: Dict[str, Any]) -> PolicyResult:
        """
        Evaluate policy for a workflow based on validation results.
        
        Args:
            validation_result: Static validation results
            wpk_data: WPK configuration data
            
        Returns:
            PolicyResult with decision and requirements
        """
        errors = []
        warnings = []
        
        # Get safety mode from WPK
        safety_mode = self._get_safety_mode(wpk_data)
        
        # Determine policy decision based on risk score and safety mode
        decision = self._determine_decision(validation_result.risk_score, safety_mode)
        
        # Check if approval is required
        approval_required = self._requires_approval(validation_result, decision)
        
        # Generate warnings for medium-risk issues
        for issue in validation_result.issues:
            if issue.severity in [Severity.MEDIUM, Severity.LOW]:
                warnings.append(f"{issue.message} at {issue.path}")
        
        # Generate errors for high-risk issues that block execution
        if decision == PolicyDecision.BLOCK:
            for issue in validation_result.issues:
                if issue.severity in [Severity.CRITICAL, Severity.HIGH]:
                    errors.append(f"{issue.message} at {issue.path}")
        
        return PolicyResult(
            valid=decision != PolicyDecision.BLOCK,
            policy_decision=decision,
            approval_required=approval_required,
            risk_score=validation_result.risk_score,
            errors=errors,
            warnings=warnings
        )
    
    def generate_approval_request(
        self,
        wpk_data: Dict[str, Any],
        policy_result: PolicyResult,
        requested_by: str = "system",
        justification: str = ""
    ) -> ApprovalRequest:
        """Generate approval request for high-risk workflows."""
        
        workflow_id = f"{wpk_data.get('metadata', {}).get('name', 'unknown')}-{wpk_data.get('metadata', {}).get('version', '1.0.0')}"
        
        # Reconstruct issues from policy result (simplified)
        issues = []
        for error in policy_result.errors:
            issues.append(ValidationIssue(
                rule_id="policy_violation",
                severity=Severity.HIGH,
                message=error,
                path="unknown"
            ))
        
        requested_at = datetime.utcnow()
        expires_at = requested_at + timedelta(hours=self.policies["approval_expiry_hours"])
        
        return ApprovalRequest(
            workflow_id=workflow_id,
            risk_score=policy_result.risk_score,
            issues=issues,
            justification=justification or f"Workflow requires approval due to risk score: {policy_result.risk_score}",
            requested_by=requested_by,
            requested_at=requested_at,
            expires_at=expires_at
        )
    
    def _get_safety_mode(self, wpk_data: Dict[str, Any]) -> SafetyMode:
        """Extract safety mode from WPK configuration."""
        safety_config = wpk_data.get("spec", {}).get("safety", {})
        mode = safety_config.get("mode", "manual").lower()
        
        try:
            return SafetyMode(mode)
        except ValueError:
            logger.warning(f"Invalid safety mode '{mode}', defaulting to manual")
            return SafetyMode.MANUAL
    
    def _determine_decision(self, risk_score: int, safety_mode: SafetyMode) -> PolicyDecision:
        """Determine policy decision based on risk score and safety mode."""
        
        # Critical risk always blocks
        if risk_score >= self.policies["block_threshold"]:
            return PolicyDecision.BLOCK
        
        # High risk requires review or blocks in auto mode
        if risk_score >= self.policies["review_threshold"]:
            if safety_mode == SafetyMode.AUTO:
                return PolicyDecision.BLOCK
            else:
                return PolicyDecision.REVIEW
        
        # Medium risk requires review in auto mode, approves in manual
        if risk_score >= self.policies["auto_approve_threshold"]:
            if safety_mode == SafetyMode.AUTO:
                return PolicyDecision.REVIEW
            else:
                return PolicyDecision.APPROVE
        
        # Low risk always approves
        return PolicyDecision.APPROVE
    
    def _requires_approval(self, validation_result: ValidationResult, decision: PolicyDecision) -> bool:
        """Determine if manual approval is required."""
        
        # Always require approval for blocked workflows
        if decision == PolicyDecision.BLOCK:
            return True
        
        # Require approval for workflows with critical issues
        if validation_result.critical_issues:
            return True
        
        # Require approval for review decisions
        if decision == PolicyDecision.REVIEW:
            return True
        
        return False
    
    def categorize_workflow(self, wpk_data: Dict[str, Any], validation_result: ValidationResult) -> Dict[str, Any]:
        """Categorize workflow based on content and risk assessment."""
        
        categories = []
        tags = wpk_data.get("metadata", {}).get("tags", [])
        
        # Categorize by tags
        if "infrastructure" in tags:
            categories.append("infrastructure")
        if "security" in tags:
            categories.append("security")
        if "monitoring" in tags:
            categories.append("monitoring")
        
        # Categorize by risk level
        risk_score = validation_result.risk_score
        if risk_score >= 75:
            risk_level = "critical"
        elif risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 25:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Categorize by resource types
        resource_types = set()
        handlers = wpk_data.get("spec", {}).get("handlers", [])
        
        for handler in handlers:
            steps = handler.get("steps", [])
            for step in steps:
                if "kubernetes" in step:
                    resource_types.add("kubernetes")
                if "container" in step:
                    resource_types.add("container")
                if "shell" in step:
                    resource_types.add("shell")
        
        return {
            "categories": categories,
            "risk_level": risk_level,
            "resource_types": list(resource_types),
            "complexity": self._assess_complexity(wpk_data),
            "automation_level": self._assess_automation_level(wpk_data)
        }
    
    def _assess_complexity(self, wpk_data: Dict[str, Any]) -> str:
        """Assess workflow complexity."""
        handlers = wpk_data.get("spec", {}).get("handlers", [])
        total_steps = sum(len(handler.get("steps", [])) for handler in handlers)
        
        if total_steps <= 3:
            return "simple"
        elif total_steps <= 10:
            return "moderate"
        else:
            return "complex"
    
    def _assess_automation_level(self, wpk_data: Dict[str, Any]) -> str:
        """Assess workflow automation level."""
        safety_mode = self._get_safety_mode(wpk_data)
        
        # Check for manual intervention points
        handlers = wpk_data.get("spec", {}).get("handlers", [])
        has_manual_steps = False
        
        for handler in handlers:
            steps = handler.get("steps", [])
            for step in steps:
                if step.get("manual", False) or step.get("approval_required", False):
                    has_manual_steps = True
                    break
        
        if safety_mode == SafetyMode.AUTO and not has_manual_steps:
            return "fully_automated"
        elif safety_mode == SafetyMode.AUTO:
            return "semi_automated"
        else:
            return "manual"

def create_policy_engine() -> PolicyEngine:
    """Factory function to create policy engine."""
    return PolicyEngine()