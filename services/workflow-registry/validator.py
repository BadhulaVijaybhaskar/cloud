"""
Registry Validator + Policy Hooks
Dry-run and policy check engine before execution
"""

import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import re
import hashlib

logger = logging.getLogger(__name__)

class SafetyMode(Enum):
    MANUAL = "manual"
    AUTO = "auto"

class PolicyDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"

class ValidationResult:
    def __init__(self, valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.policy_decision = PolicyDecision.ALLOW
        self.approval_required = False
        self.risk_score = 0

class PolicyEngine:
    """Policy engine for workflow validation and approval"""
    
    def __init__(self):
        self.policies = self.load_default_policies()
        self.approval_cache = {}  # Cache for approval decisions
    
    def load_default_policies(self) -> Dict[str, Any]:
        """Load default security and safety policies"""
        return {
            "safety_policies": {
                "default_mode": "manual",
                "auto_allowed_namespaces": ["development", "staging"],
                "auto_denied_namespaces": ["production"],
                "require_approval_for_auto": True
            },
            "resource_policies": {
                "max_replicas": 50,
                "max_cpu": "4000m",
                "max_memory": "8Gi",
                "allowed_images": ["nginx", "busybox", "alpine"],
                "denied_images": ["latest", "debug"],
                "max_job_duration": "1h"
            },
            "security_policies": {
                "require_signature": True,
                "require_rbac_validation": True,
                "deny_privileged": True,
                "require_network_policies": False,
                "max_risk_score": 7
            },
            "operational_policies": {
                "require_rollback": True,
                "require_monitoring": True,
                "max_execution_time": "30m",
                "require_dry_run_for_auto": True
            }
        }
    
    def evaluate_safety_policy(self, wpk_content: Dict[str, Any]) -> Tuple[PolicyDecision, List[str]]:
        """Evaluate safety mode policies"""
        reasons = []
        safety_mode = wpk_content.get("spec", {}).get("safety", {}).get("mode", "manual")
        
        # Check if auto mode is allowed
        if safety_mode == SafetyMode.AUTO.value:
            # Check namespace restrictions
            handlers = wpk_content.get("spec", {}).get("handlers", [])
            for handler in handlers:
                if handler.get("type") == "k8s":
                    namespace = handler.get("config", {}).get("namespace", "default")
                    
                    if namespace in self.policies["safety_policies"]["auto_denied_namespaces"]:
                        reasons.append(f"Auto mode denied for namespace: {namespace}")
                        return PolicyDecision.DENY, reasons
                    
                    if namespace not in self.policies["safety_policies"]["auto_allowed_namespaces"]:
                        reasons.append(f"Auto mode requires approval for namespace: {namespace}")
                        return PolicyDecision.REQUIRE_APPROVAL, reasons
            
            # Check if approval is required for auto mode
            if self.policies["safety_policies"]["require_approval_for_auto"]:
                reasons.append("Auto mode requires org-admin approval")
                return PolicyDecision.REQUIRE_APPROVAL, reasons
        
        return PolicyDecision.ALLOW, reasons
    
    def evaluate_resource_policy(self, wpk_content: Dict[str, Any]) -> Tuple[PolicyDecision, List[str]]:
        """Evaluate resource usage policies"""
        reasons = []
        
        # Check resource limits
        runtime_req = wpk_content.get("spec", {}).get("runtime", {}).get("requirements", {})
        
        if "cpu" in runtime_req:
            cpu = runtime_req["cpu"]
            if self._compare_resource(cpu, self.policies["resource_policies"]["max_cpu"]) > 0:
                reasons.append(f"CPU request {cpu} exceeds limit {self.policies['resource_policies']['max_cpu']}")
                return PolicyDecision.DENY, reasons
        
        if "memory" in runtime_req:
            memory = runtime_req["memory"]
            if self._compare_resource(memory, self.policies["resource_policies"]["max_memory"]) > 0:
                reasons.append(f"Memory request {memory} exceeds limit {self.policies['resource_policies']['max_memory']}")
                return PolicyDecision.DENY, reasons
        
        # Check handlers for resource usage
        handlers = wpk_content.get("spec", {}).get("handlers", [])
        for handler in handlers:
            if handler.get("type") == "k8s":
                config = handler.get("config", {})
                
                # Check scaling limits
                if "replicas" in config:
                    replicas = config["replicas"]
                    if replicas > self.policies["resource_policies"]["max_replicas"]:
                        reasons.append(f"Replica count {replicas} exceeds limit {self.policies['resource_policies']['max_replicas']}")
                        return PolicyDecision.DENY, reasons
                
                # Check image policies
                if "image" in config:
                    image = config["image"]
                    if any(denied in image for denied in self.policies["resource_policies"]["denied_images"]):
                        reasons.append(f"Image {image} contains denied tags")
                        return PolicyDecision.DENY, reasons
        
        return PolicyDecision.ALLOW, reasons
    
    def evaluate_security_policy(self, wpk_content: Dict[str, Any]) -> Tuple[PolicyDecision, List[str]]:
        """Evaluate security policies"""
        reasons = []
        
        # Check signature requirement
        if self.policies["security_policies"]["require_signature"]:
            signature = wpk_content.get("metadata", {}).get("signature")
            if not signature:
                reasons.append("Workflow must be signed")
                return PolicyDecision.DENY, reasons
        
        # Check for privileged operations
        if self.policies["security_policies"]["deny_privileged"]:
            handlers = wpk_content.get("spec", {}).get("handlers", [])
            for handler in handlers:
                config = handler.get("config", {})
                if config.get("privileged", False):
                    reasons.append("Privileged operations are not allowed")
                    return PolicyDecision.DENY, reasons
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(wpk_content)
        if risk_score > self.policies["security_policies"]["max_risk_score"]:
            reasons.append(f"Risk score {risk_score} exceeds maximum {self.policies['security_policies']['max_risk_score']}")
            return PolicyDecision.REQUIRE_APPROVAL, reasons
        
        return PolicyDecision.ALLOW, reasons
    
    def evaluate_operational_policy(self, wpk_content: Dict[str, Any]) -> Tuple[PolicyDecision, List[str]]:
        """Evaluate operational policies"""
        reasons = []
        
        # Check rollback requirement
        if self.policies["operational_policies"]["require_rollback"]:
            rollback = wpk_content.get("spec", {}).get("rollback", {})
            if not rollback.get("enabled", False):
                reasons.append("Rollback must be enabled")
                return PolicyDecision.REQUIRE_APPROVAL, reasons
        
        # Check monitoring requirement
        if self.policies["operational_policies"]["require_monitoring"]:
            monitoring = wpk_content.get("spec", {}).get("monitoring", {})
            if not monitoring.get("metrics_enabled", False):
                reasons.append("Monitoring must be enabled")
                return PolicyDecision.REQUIRE_APPROVAL, reasons
        
        # Check dry-run requirement for auto mode
        safety_mode = wpk_content.get("spec", {}).get("safety", {}).get("mode", "manual")
        if (safety_mode == SafetyMode.AUTO.value and 
            self.policies["operational_policies"]["require_dry_run_for_auto"]):
            dry_run_required = wpk_content.get("spec", {}).get("safety", {}).get("dry_run_required", False)
            if not dry_run_required:
                reasons.append("Dry-run required for auto mode workflows")
                return PolicyDecision.REQUIRE_APPROVAL, reasons
        
        return PolicyDecision.ALLOW, reasons
    
    def _compare_resource(self, value: str, limit: str) -> int:
        """Compare resource values (simplified)"""
        # Simple comparison - in production, use proper resource parsing
        value_num = int(re.findall(r'\d+', value)[0]) if re.findall(r'\d+', value) else 0
        limit_num = int(re.findall(r'\d+', limit)[0]) if re.findall(r'\d+', limit) else 0
        return value_num - limit_num
    
    def _calculate_risk_score(self, wpk_content: Dict[str, Any]) -> int:
        """Calculate risk score for workflow"""
        risk_score = 0
        
        # Base risk factors
        handlers = wpk_content.get("spec", {}).get("handlers", [])
        risk_score += len(handlers)  # More handlers = higher risk
        
        # Handler type risks
        for handler in handlers:
            handler_type = handler.get("type", "")
            if handler_type == "shell":
                risk_score += 3  # Shell commands are risky
            elif handler_type == "k8s":
                risk_score += 1  # K8s operations are moderate risk
            elif handler_type == "api":
                risk_score += 2  # API calls are moderate-high risk
        
        # Safety mode risk
        safety_mode = wpk_content.get("spec", {}).get("safety", {}).get("mode", "manual")
        if safety_mode == SafetyMode.AUTO.value:
            risk_score += 2
        
        # Rollback availability
        rollback_enabled = wpk_content.get("spec", {}).get("rollback", {}).get("enabled", False)
        if not rollback_enabled:
            risk_score += 2
        
        return risk_score

class WorkflowValidator:
    """Main validator class for workflows"""
    
    def __init__(self):
        self.policy_engine = PolicyEngine()
    
    def validate_wpk_structure(self, wpk_content: Dict[str, Any]) -> ValidationResult:
        """Validate WPK structure and schema"""
        errors = []
        warnings = []
        
        # Check required top-level fields
        required_fields = ["apiVersion", "kind", "metadata", "spec"]
        for field in required_fields:
            if field not in wpk_content:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return ValidationResult(False, errors, warnings)
        
        # Validate metadata
        metadata = wpk_content.get("metadata", {})
        required_metadata = ["name", "version", "description", "author"]
        for field in required_metadata:
            if field not in metadata:
                errors.append(f"Missing metadata field: {field}")
        
        # Validate version format
        version = metadata.get("version", "")
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"Invalid version format: {version} (expected: x.y.z)")
        
        # Validate spec
        spec = wpk_content.get("spec", {})
        required_spec = ["runtime", "safety", "handlers"]
        for field in required_spec:
            if field not in spec:
                errors.append(f"Missing spec field: {field}")
        
        # Validate handlers
        handlers = spec.get("handlers", [])
        if not handlers:
            errors.append("No handlers defined")
        
        for i, handler in enumerate(handlers):
            handler_errors = self._validate_handler(handler, i)
            errors.extend(handler_errors)
        
        # Validate safety configuration
        safety = spec.get("safety", {})
        if "mode" not in safety:
            errors.append("Safety mode not specified")
        elif safety["mode"] not in [SafetyMode.MANUAL.value, SafetyMode.AUTO.value]:
            errors.append(f"Invalid safety mode: {safety['mode']}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def _validate_handler(self, handler: Dict[str, Any], index: int) -> List[str]:
        """Validate individual handler"""
        errors = []
        
        required_fields = ["name", "type", "config"]
        for field in required_fields:
            if field not in handler:
                errors.append(f"Handler {index}: missing {field}")
        
        # Validate handler type
        handler_type = handler.get("type", "")
        valid_types = ["k8s", "shell", "api"]
        if handler_type not in valid_types:
            errors.append(f"Handler {index}: invalid type '{handler_type}' (valid: {valid_types})")
        
        # Validate timeout format
        timeout = handler.get("timeout", "")
        if timeout and not re.match(r'^\d+[smh]?$', timeout):
            errors.append(f"Handler {index}: invalid timeout format '{timeout}'")
        
        return errors
    
    def validate_policies(self, wpk_content: Dict[str, Any]) -> ValidationResult:
        """Validate workflow against policies"""
        result = ValidationResult(True)
        all_reasons = []
        
        # Evaluate all policy categories
        policy_checks = [
            self.policy_engine.evaluate_safety_policy,
            self.policy_engine.evaluate_resource_policy,
            self.policy_engine.evaluate_security_policy,
            self.policy_engine.evaluate_operational_policy
        ]
        
        for policy_check in policy_checks:
            decision, reasons = policy_check(wpk_content)
            all_reasons.extend(reasons)
            
            if decision == PolicyDecision.DENY:
                result.valid = False
                result.policy_decision = PolicyDecision.DENY
                result.errors.extend(reasons)
            elif decision == PolicyDecision.REQUIRE_APPROVAL:
                result.approval_required = True
                result.policy_decision = PolicyDecision.REQUIRE_APPROVAL
                result.warnings.extend(reasons)
        
        # Calculate overall risk score
        result.risk_score = self.policy_engine._calculate_risk_score(wpk_content)
        
        return result
    
    def dry_run_validation(self, wpk_content: Dict[str, Any], parameters: Dict[str, Any] = None) -> ValidationResult:
        """Perform dry-run validation"""
        result = ValidationResult(True)
        warnings = []
        
        # Simulate handler execution
        handlers = wpk_content.get("spec", {}).get("handlers", [])
        
        for i, handler in enumerate(handlers):
            handler_type = handler.get("type", "")
            config = handler.get("config", {})
            
            # Validate handler configuration
            if handler_type == "k8s":
                k8s_warnings = self._validate_k8s_handler_dry_run(config)
                warnings.extend(k8s_warnings)
            elif handler_type == "shell":
                shell_warnings = self._validate_shell_handler_dry_run(config)
                warnings.extend(shell_warnings)
            elif handler_type == "api":
                api_warnings = self._validate_api_handler_dry_run(config)
                warnings.extend(api_warnings)
        
        result.warnings = warnings
        return result
    
    def _validate_k8s_handler_dry_run(self, config: Dict[str, Any]) -> List[str]:
        """Validate k8s handler in dry-run mode"""
        warnings = []
        
        action = config.get("action", "")
        if action == "scale":
            replicas = config.get("replicas", 1)
            if replicas > 10:
                warnings.append(f"Scaling to {replicas} replicas may impact cluster resources")
        
        elif action == "restart":
            resource_type = config.get("resource_type", "")
            if resource_type == "deployment":
                warnings.append("Deployment restart will cause temporary service disruption")
        
        return warnings
    
    def _validate_shell_handler_dry_run(self, config: Dict[str, Any]) -> List[str]:
        """Validate shell handler in dry-run mode"""
        warnings = []
        
        command = config.get("command", "")
        
        # Check for potentially dangerous commands
        dangerous_patterns = ["rm -rf", "dd if=", "mkfs", "fdisk", "shutdown", "reboot"]
        for pattern in dangerous_patterns:
            if pattern in command:
                warnings.append(f"Potentially dangerous command detected: {pattern}")
        
        # Check for network operations
        network_patterns = ["curl", "wget", "ssh", "scp", "rsync"]
        for pattern in network_patterns:
            if pattern in command:
                warnings.append(f"Network operation detected: {pattern}")
        
        return warnings
    
    def _validate_api_handler_dry_run(self, config: Dict[str, Any]) -> List[str]:
        """Validate API handler in dry-run mode"""
        warnings = []
        
        url = config.get("url", "")
        method = config.get("method", "GET")
        
        # Check for external URLs
        if not any(domain in url for domain in ["localhost", "127.0.0.1", "internal"]):
            warnings.append(f"External API call detected: {url}")
        
        # Check for destructive methods
        if method in ["DELETE", "PUT", "PATCH"]:
            warnings.append(f"Potentially destructive HTTP method: {method}")
        
        return warnings
    
    def generate_approval_request(self, wpk_content: Dict[str, Any], validation_result: ValidationResult) -> Dict[str, Any]:
        """Generate approval request for workflows requiring approval"""
        workflow_name = wpk_content.get("metadata", {}).get("name", "unknown")
        workflow_version = wpk_content.get("metadata", {}).get("version", "unknown")
        
        approval_request = {
            "workflow_id": f"{workflow_name}-{workflow_version}",
            "workflow_name": workflow_name,
            "workflow_version": workflow_version,
            "author": wpk_content.get("metadata", {}).get("author", "unknown"),
            "safety_mode": wpk_content.get("spec", {}).get("safety", {}).get("mode", "manual"),
            "risk_score": validation_result.risk_score,
            "policy_decision": validation_result.policy_decision.value,
            "reasons": validation_result.warnings,
            "requested_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "approver": None,
            "approved_at": None
        }
        
        return approval_request
    
    def categorize_workflow(self, wpk_content: Dict[str, Any]) -> str:
        """Categorize workflow as manual or auto based on content analysis"""
        safety_mode = wpk_content.get("spec", {}).get("safety", {}).get("mode", "manual")
        
        # If explicitly set to auto, check if it meets auto criteria
        if safety_mode == SafetyMode.AUTO.value:
            validation_result = self.validate_policies(wpk_content)
            
            if validation_result.policy_decision == PolicyDecision.ALLOW and validation_result.risk_score <= 5:
                return "auto"
            else:
                return "manual"  # Downgrade to manual if policies fail
        
        return "manual"

# Factory function
def create_validator() -> WorkflowValidator:
    """Create a new workflow validator instance"""
    return WorkflowValidator()