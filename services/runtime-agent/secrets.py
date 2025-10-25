"""
Vault integration for ATOM runtime agent.

Provides secure access to secrets required for workflow execution,
including Kubernetes credentials, API tokens, and service keys.

Usage:
    from secrets import get_kubernetes_config, get_api_credentials
    
    kubeconfig = get_kubernetes_config()
    api_token = get_api_credentials("external-service")

Security Notes:
    - Secrets are retrieved on-demand and not cached
    - Use service account authentication in production
    - Implement secret rotation policies
    - Monitor secret access logs
"""

import os
import logging
from typing import Optional, Dict, Any
import tempfile
from pathlib import Path

# Import Vault client from workflow-registry
import sys
sys.path.append(str(Path(__file__).parent.parent / "workflow-registry"))

try:
    from secrets import VaultClient, create_vault_client
except ImportError:
    # Fallback if Vault client not available
    VaultClient = None
    create_vault_client = lambda: None

logger = logging.getLogger(__name__)

def get_kubernetes_config() -> Optional[str]:
    """
    Get Kubernetes configuration from Vault or environment.
    
    Returns:
        Kubeconfig content as string or None if not available
    """
    vault = create_vault_client() if create_vault_client else None
    
    if vault:
        try:
            return vault.get_secret("atom/kubernetes", "config")
        except Exception as e:
            logger.warning(f"Failed to get kubeconfig from Vault: {e}")
    
    # Fallback to environment variable or default location
    kubeconfig_path = os.getenv("KUBECONFIG", os.path.expanduser("~/.kube/config"))
    
    if os.path.exists(kubeconfig_path):
        try:
            with open(kubeconfig_path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read kubeconfig from {kubeconfig_path}: {e}")
    
    return None

def get_api_credentials(service_name: str) -> Optional[Dict[str, str]]:
    """
    Get API credentials for external services.
    
    Args:
        service_name: Name of the service (e.g., "prometheus", "grafana")
        
    Returns:
        Dictionary with credentials or None if not available
    """
    vault = create_vault_client() if create_vault_client else None
    
    if vault:
        try:
            return vault.get_secret(f"atom/api/{service_name}")
        except Exception as e:
            logger.warning(f"Failed to get {service_name} credentials from Vault: {e}")
    
    # Fallback to environment variables
    env_prefix = service_name.upper().replace("-", "_")
    return {
        "username": os.getenv(f"{env_prefix}_USERNAME"),
        "password": os.getenv(f"{env_prefix}_PASSWORD"),
        "token": os.getenv(f"{env_prefix}_TOKEN"),
        "url": os.getenv(f"{env_prefix}_URL")
    }

def get_workflow_secrets(workflow_id: str) -> Optional[Dict[str, Any]]:
    """
    Get workflow-specific secrets from Vault.
    
    Args:
        workflow_id: Unique workflow identifier
        
    Returns:
        Dictionary with workflow secrets or None if not available
    """
    vault = create_vault_client() if create_vault_client else None
    
    if vault:
        try:
            return vault.get_secret(f"atom/workflows/{workflow_id}")
        except Exception as e:
            logger.warning(f"Failed to get secrets for workflow {workflow_id}: {e}")
    
    return None

def create_temporary_kubeconfig() -> Optional[str]:
    """
    Create temporary kubeconfig file from Vault secrets.
    
    Returns:
        Path to temporary kubeconfig file or None if failed
    """
    kubeconfig_content = get_kubernetes_config()
    
    if not kubeconfig_content:
        return None
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.kubeconfig', delete=False) as f:
            f.write(kubeconfig_content)
            temp_path = f.name
        
        logger.info(f"Created temporary kubeconfig at {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.error(f"Failed to create temporary kubeconfig: {e}")
        return None

def cleanup_temporary_file(file_path: str):
    """Clean up temporary files securely."""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.debug(f"Cleaned up temporary file {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temporary file {file_path}: {e}")

def get_monitoring_credentials() -> Dict[str, Optional[str]]:
    """Get monitoring system credentials (Prometheus, Grafana, etc.)."""
    return {
        "prometheus_url": get_api_credentials("prometheus").get("url") if get_api_credentials("prometheus") else os.getenv("PROMETHEUS_URL"),
        "grafana_token": get_api_credentials("grafana").get("token") if get_api_credentials("grafana") else os.getenv("GRAFANA_TOKEN"),
        "alertmanager_url": get_api_credentials("alertmanager").get("url") if get_api_credentials("alertmanager") else os.getenv("ALERTMANAGER_URL")
    }

def health_check() -> Dict[str, bool]:
    """Check health of secret management systems."""
    vault = create_vault_client() if create_vault_client else None
    
    return {
        "vault_available": vault is not None,
        "vault_healthy": vault.health_check() if vault else False,
        "kubeconfig_available": get_kubernetes_config() is not None,
        "fallback_env_vars": bool(os.getenv("KUBECONFIG") or os.path.exists(os.path.expanduser("~/.kube/config")))
    }