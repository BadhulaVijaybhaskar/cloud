"""
Static validator for WPK packages.
Performs security checks and policy validation without execution.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ValidationIssue:
    """Represents a validation issue found in WPK."""
    rule_id: str
    severity: Severity
    message: str
    path: str
    suggestion: Optional[str] = None
    cwe: Optional[str] = None

@dataclass
class ValidationResult:
    """Result of static validation."""
    valid: bool
    issues: List[ValidationIssue]
    risk_score: int
    
    @property
    def critical_issues(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.CRITICAL]
    
    @property
    def high_issues(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.HIGH]

class StaticValidator:
    """Static security and policy validator for WPK packages."""
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Dict]:
        """Load validation rules."""
        return {
            "privileged_container": {
                "severity": Severity.CRITICAL,
                "message": "Privileged containers are not allowed",
                "suggestion": "Use specific capabilities instead of privileged mode",
                "cwe": "CWE-250"
            },
            "host_path_mount": {
                "severity": Severity.CRITICAL,
                "message": "Host path mounts to sensitive directories are not allowed",
                "suggestion": "Use persistent volumes or configmaps instead",
                "cwe": "CWE-22"
            },
            "dangerous_capabilities": {
                "severity": Severity.CRITICAL,
                "message": "Dangerous Linux capabilities detected",
                "suggestion": "Remove unnecessary capabilities or use least privilege",
                "cwe": "CWE-250"
            },
            "cluster_permissions": {
                "severity": Severity.HIGH,
                "message": "Cluster-level permissions detected",
                "suggestion": "Use namespace-scoped permissions when possible",
                "cwe": "CWE-269"
            },
            "external_network": {
                "severity": Severity.HIGH,
                "message": "External network access detected",
                "suggestion": "Use internal services or whitelist specific domains",
                "cwe": "CWE-918"
            },
            "excessive_resources": {
                "severity": Severity.MEDIUM,
                "message": "Excessive resource requests detected",
                "suggestion": "Optimize resource usage based on actual requirements",
                "cwe": "CWE-400"
            },
            "missing_limits": {
                "severity": Severity.MEDIUM,
                "message": "Missing resource limits",
                "suggestion": "Add resource limits to prevent resource exhaustion",
                "cwe": "CWE-400"
            },
            "hardcoded_secrets": {
                "severity": Severity.HIGH,
                "message": "Hardcoded secrets detected",
                "suggestion": "Use Kubernetes secrets or external secret management",
                "cwe": "CWE-798"
            },
            "insecure_image": {
                "severity": Severity.MEDIUM,
                "message": "Insecure container image configuration",
                "suggestion": "Use pinned image tags and trusted registries",
                "cwe": "CWE-829"
            }
        }
    
    def validate(self, wpk_data: Dict[str, Any]) -> ValidationResult:
        """
        Perform static validation on WPK data.
        
        Args:
            wpk_data: Parsed WPK YAML data
            
        Returns:
            ValidationResult with issues and risk score
        """
        issues = []
        
        # Check handlers and steps
        handlers = wpk_data.get("spec", {}).get("handlers", [])
        for i, handler in enumerate(handlers):
            handler_path = f"spec.handlers[{i}]"
            issues.extend(self._validate_handler(handler, handler_path))
        
        # Check runtime configuration
        runtime = wpk_data.get("spec", {}).get("runtime", {})
        issues.extend(self._validate_runtime(runtime, "spec.runtime"))
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(issues)
        
        # Determine if validation passes
        valid = risk_score < 76  # Block critical risk workflows
        
        return ValidationResult(
            valid=valid,
            issues=issues,
            risk_score=risk_score
        )
    
    def _validate_handler(self, handler: Dict[str, Any], path: str) -> List[ValidationIssue]:
        """Validate a single handler."""
        issues = []
        
        steps = handler.get("steps", [])
        for i, step in enumerate(steps):
            step_path = f"{path}.steps[{i}]"
            issues.extend(self._validate_step(step, step_path))
        
        return issues
    
    def _validate_step(self, step: Dict[str, Any], path: str) -> List[ValidationIssue]:
        """Validate a single step."""
        issues = []
        
        # Check container configuration
        if "container" in step:
            issues.extend(self._validate_container(step["container"], f"{path}.container"))
        
        # Check Kubernetes resources
        if "kubernetes" in step:
            issues.extend(self._validate_kubernetes(step["kubernetes"], f"{path}.kubernetes"))
        
        # Check shell commands
        if "shell" in step:
            issues.extend(self._validate_shell(step["shell"], f"{path}.shell"))
        
        return issues
    
    def _validate_container(self, container: Dict[str, Any], path: str) -> List[ValidationIssue]:
        """Validate container configuration."""
        issues = []
        
        # Check privileged mode
        security_context = container.get("securityContext", {})
        if security_context.get("privileged", False):
            issues.append(ValidationIssue(
                rule_id="privileged_container",
                severity=self.rules["privileged_container"]["severity"],
                message=self.rules["privileged_container"]["message"],
                path=f"{path}.securityContext.privileged",
                suggestion=self.rules["privileged_container"]["suggestion"],
                cwe=self.rules["privileged_container"]["cwe"]
            ))
        
        # Check dangerous capabilities
        capabilities = security_context.get("capabilities", {})
        dangerous_caps = {"CAP_SYS_ADMIN", "CAP_NET_ADMIN", "CAP_SYS_PTRACE", "CAP_SYS_MODULE"}
        add_caps = set(capabilities.get("add", []))
        
        if dangerous_caps & add_caps:
            found_caps = dangerous_caps & add_caps
            issues.append(ValidationIssue(
                rule_id="dangerous_capabilities",
                severity=self.rules["dangerous_capabilities"]["severity"],
                message=f"{self.rules['dangerous_capabilities']['message']}: {', '.join(found_caps)}",
                path=f"{path}.securityContext.capabilities.add",
                suggestion=self.rules["dangerous_capabilities"]["suggestion"],
                cwe=self.rules["dangerous_capabilities"]["cwe"]
            ))
        
        # Check volume mounts
        volume_mounts = container.get("volumeMounts", [])
        for i, mount in enumerate(volume_mounts):
            mount_path = mount.get("mountPath", "")
            if self._is_sensitive_path(mount_path):
                issues.append(ValidationIssue(
                    rule_id="host_path_mount",
                    severity=self.rules["host_path_mount"]["severity"],
                    message=f"{self.rules['host_path_mount']['message']}: {mount_path}",
                    path=f"{path}.volumeMounts[{i}].mountPath",
                    suggestion=self.rules["host_path_mount"]["suggestion"],
                    cwe=self.rules["host_path_mount"]["cwe"]
                ))
        
        # Check resource limits
        resources = container.get("resources", {})
        issues.extend(self._validate_resources(resources, f"{path}.resources"))
        
        # Check image security
        image = container.get("image", "")
        issues.extend(self._validate_image(image, f"{path}.image"))
        
        return issues
    
    def _validate_kubernetes(self, k8s_config: Dict[str, Any], path: str) -> List[ValidationIssue]:
        """Validate Kubernetes resource configuration."""
        issues = []
        
        # Check for cluster-level resources
        kind = k8s_config.get("kind", "")
        if kind in ["ClusterRole", "ClusterRoleBinding"]:
            issues.append(ValidationIssue(
                rule_id="cluster_permissions",
                severity=self.rules["cluster_permissions"]["severity"],
                message=f"{self.rules['cluster_permissions']['message']}: {kind}",
                path=f"{path}.kind",
                suggestion=self.rules["cluster_permissions"]["suggestion"],
                cwe=self.rules["cluster_permissions"]["cwe"]
            ))
        
        return issues
    
    def _validate_shell(self, shell_config: Dict[str, Any], path: str) -> List[ValidationIssue]:
        """Validate shell command configuration."""
        issues = []
        
        command = shell_config.get("command", "")
        
        # Check for external network calls
        if self._has_external_network_call(command):
            issues.append(ValidationIssue(
                rule_id="external_network",
                severity=self.rules["external_network"]["severity"],
                message=self.rules["external_network"]["message"],
                path=f"{path}.command",
                suggestion=self.rules["external_network"]["suggestion"],
                cwe=self.rules["external_network"]["cwe"]
            ))
        
        # Check for hardcoded secrets
        if self._has_hardcoded_secrets(command):
            issues.append(ValidationIssue(
                rule_id="hardcoded_secrets",
                severity=self.rules["hardcoded_secrets"]["severity"],
                message=self.rules["hardcoded_secrets"]["message"],
                path=f"{path}.command",
                suggestion=self.rules["hardcoded_secrets"]["suggestion"],
                cwe=self.rules["hardcoded_secrets"]["cwe"]
            ))
        
        return issues
    
    def _validate_runtime(self, runtime: Dict[str, Any], path: str) -> List[ValidationIssue]:
        """Validate runtime configuration."""
        issues = []
        
        # Additional runtime-specific validations can be added here
        
        return issues
    
    def _validate_resources(self, resources: Dict[str, Any], path: str) -> List[ValidationIssue]:
        """Validate resource configuration."""
        issues = []
        
        requests = resources.get("requests", {})
        limits = resources.get("limits", {})
        
        # Check for missing limits
        if not limits:
            issues.append(ValidationIssue(
                rule_id="missing_limits",
                severity=self.rules["missing_limits"]["severity"],
                message=self.rules["missing_limits"]["message"],
                path=path,
                suggestion=self.rules["missing_limits"]["suggestion"],
                cwe=self.rules["missing_limits"]["cwe"]
            ))
        
        # Check for excessive resources
        cpu_limit = limits.get("cpu", "")
        memory_limit = limits.get("memory", "")
        
        if self._is_excessive_cpu(cpu_limit):
            issues.append(ValidationIssue(
                rule_id="excessive_resources",
                severity=self.rules["excessive_resources"]["severity"],
                message=f"{self.rules['excessive_resources']['message']}: CPU {cpu_limit}",
                path=f"{path}.limits.cpu",
                suggestion=self.rules["excessive_resources"]["suggestion"],
                cwe=self.rules["excessive_resources"]["cwe"]
            ))
        
        if self._is_excessive_memory(memory_limit):
            issues.append(ValidationIssue(
                rule_id="excessive_resources",
                severity=self.rules["excessive_resources"]["severity"],
                message=f"{self.rules['excessive_resources']['message']}: Memory {memory_limit}",
                path=f"{path}.limits.memory",
                suggestion=self.rules["excessive_resources"]["suggestion"],
                cwe=self.rules["excessive_resources"]["cwe"]
            ))
        
        return issues
    
    def _validate_image(self, image: str, path: str) -> List[ValidationIssue]:
        """Validate container image configuration."""
        issues = []
        
        # Check for latest tag
        if image.endswith(":latest") or ":" not in image:
            issues.append(ValidationIssue(
                rule_id="insecure_image",
                severity=self.rules["insecure_image"]["severity"],
                message=f"{self.rules['insecure_image']['message']}: using latest tag",
                path=path,
                suggestion="Use specific image tags for reproducible builds",
                cwe=self.rules["insecure_image"]["cwe"]
            ))
        
        return issues
    
    def _is_sensitive_path(self, path: str) -> bool:
        """Check if path is sensitive for host mounts."""
        sensitive_paths = {
            "/", "/etc", "/var/run/docker.sock", "/proc", "/sys",
            "/var/lib/docker", "/var/lib/kubelet", "/etc/kubernetes"
        }
        return path in sensitive_paths or path.startswith("/var/run/")
    
    def _has_external_network_call(self, command: str) -> bool:
        """Check if command contains external network calls."""
        patterns = [
            r'(curl|wget)\s+.*https?://(?!localhost|127\.0\.0\.1|10\.|172\.|192\.168\.)',
            r'(nc|netcat)\s+.*\.(com|org|net|io)',
            r'(ssh|scp)\s+.*@.*\.(com|org|net|io)'
        ]
        
        for pattern in patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False
    
    def _has_hardcoded_secrets(self, command: str) -> bool:
        """Check if command contains hardcoded secrets."""
        patterns = [
            r'(password|secret|key|token)\s*[:=]\s*[\'"][^\'"\s]{8,}[\'"]',
            r'(api_key|access_key|private_key)\s*[:=]',
            r'[\'"][A-Za-z0-9+/]{20,}={0,2}[\'"]'  # Base64 patterns
        ]
        
        for pattern in patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False
    
    def _is_excessive_cpu(self, cpu: str) -> bool:
        """Check if CPU limit is excessive."""
        if not cpu:
            return False
        
        # Parse CPU values (e.g., "4", "4000m", "4.5")
        try:
            if cpu.endswith("m"):
                cpu_val = float(cpu[:-1]) / 1000
            else:
                cpu_val = float(cpu)
            return cpu_val > 4.0
        except ValueError:
            return False
    
    def _is_excessive_memory(self, memory: str) -> bool:
        """Check if memory limit is excessive."""
        if not memory:
            return False
        
        # Parse memory values (e.g., "8Gi", "8192Mi", "8589934592")
        try:
            memory_upper = memory.upper()
            if memory_upper.endswith("GI"):
                mem_val = float(memory_upper[:-2])
                return mem_val > 8.0
            elif memory_upper.endswith("MI"):
                mem_val = float(memory_upper[:-2]) / 1024
                return mem_val > 8.0
            elif memory_upper.endswith("G"):
                mem_val = float(memory_upper[:-1])
                return mem_val > 8.0
            elif memory_upper.endswith("M"):
                mem_val = float(memory_upper[:-1]) / 1024
                return mem_val > 8.0
        except ValueError:
            pass
        return False
    
    def _calculate_risk_score(self, issues: List[ValidationIssue]) -> int:
        """Calculate overall risk score based on issues."""
        base_score = 0
        multiplier = 1.0
        
        severity_scores = {
            Severity.CRITICAL: 25,
            Severity.HIGH: 15,
            Severity.MEDIUM: 10,
            Severity.LOW: 5
        }
        
        # Calculate base score
        for issue in issues:
            base_score += severity_scores.get(issue.severity, 0)
        
        # Apply multipliers for specific risk patterns
        rule_ids = {issue.rule_id for issue in issues}
        
        if "privileged_container" in rule_ids:
            multiplier *= 1.5
        
        if "external_network" in rule_ids:
            multiplier *= 1.2
        
        if "cluster_permissions" in rule_ids:
            multiplier *= 1.3
        
        if "hardcoded_secrets" in rule_ids:
            multiplier *= 1.4
        
        return min(100, int(base_score * multiplier))

def create_static_validator() -> StaticValidator:
    """Factory function to create static validator."""
    return StaticValidator()