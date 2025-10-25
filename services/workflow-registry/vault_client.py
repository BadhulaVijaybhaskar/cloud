"""
Vault client for secure secret management in ATOM workflow registry.

This module provides secure access to secrets stored in HashiCorp Vault,
including cosign keys, database credentials, and S3 access keys.

Usage:
    from secrets import VaultClient
    
    vault = VaultClient()
    cosign_key = vault.get_secret("cosign", "public_key")
    db_dsn = vault.get_secret("database", "dsn")

Environment Variables:
    VAULT_ADDR: Vault server address (e.g., https://vault.example.com:8200)
    VAULT_TOKEN: Vault authentication token
    VAULT_ROLE_ID: AppRole role ID (alternative to token)
    VAULT_SECRET_ID: AppRole secret ID (alternative to token)
    VAULT_NAMESPACE: Vault namespace (for Vault Enterprise)

Security Notes:
    - Never log secret values
    - Use short-lived tokens when possible
    - Rotate credentials regularly
    - Use AppRole authentication in production
"""

import os
import logging
from typing import Optional, Dict, Any
import requests
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class VaultClient:
    """HashiCorp Vault client for secure secret retrieval."""
    
    def __init__(self, vault_addr: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize Vault client.
        
        Args:
            vault_addr: Vault server address
            token: Vault authentication token
        """
        self.vault_addr = vault_addr or os.getenv("VAULT_ADDR")
        self.token = token or os.getenv("VAULT_TOKEN")
        self.namespace = os.getenv("VAULT_NAMESPACE")
        
        if not self.vault_addr:
            raise ValueError("VAULT_ADDR environment variable or vault_addr parameter required")
        
        # Remove trailing slash
        self.vault_addr = self.vault_addr.rstrip("/")
        
        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
        
        if self.namespace:
            self.session.headers["X-Vault-Namespace"] = self.namespace
        
        # Authenticate if token not provided
        if not self.token:
            self._authenticate_approle()
        else:
            self.session.headers["X-Vault-Token"] = self.token
    
    def _authenticate_approle(self):
        """Authenticate using AppRole method."""
        role_id = os.getenv("VAULT_ROLE_ID")
        secret_id = os.getenv("VAULT_SECRET_ID")
        
        if not role_id or not secret_id:
            raise ValueError("VAULT_ROLE_ID and VAULT_SECRET_ID required for AppRole authentication")
        
        auth_data = {
            "role_id": role_id,
            "secret_id": secret_id
        }
        
        try:
            response = self.session.post(
                f"{self.vault_addr}/v1/auth/approle/login",
                json=auth_data,
                timeout=10
            )
            response.raise_for_status()
            
            auth_response = response.json()
            self.token = auth_response["auth"]["client_token"]
            self.session.headers["X-Vault-Token"] = self.token
            
            logger.info("Successfully authenticated with Vault using AppRole")
            
        except requests.RequestException as e:
            logger.error(f"Failed to authenticate with Vault: {e}")
            raise
    
    def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """
        Retrieve secret from Vault KV store.
        
        Args:
            path: Secret path (e.g., "atom/cosign" for secret/atom/cosign)
            key: Specific key within the secret (optional)
            
        Returns:
            Secret value or entire secret dict if key not specified
        """
        try:
            # Use KV v2 API format
            api_path = f"v1/secret/data/{path}"
            
            response = self.session.get(
                f"{self.vault_addr}/{api_path}",
                timeout=10
            )
            response.raise_for_status()
            
            secret_data = response.json()
            data = secret_data.get("data", {}).get("data", {})
            
            if key:
                if key not in data:
                    raise KeyError(f"Key '{key}' not found in secret '{path}'")
                return data[key]
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve secret '{path}': {e}")
            raise
        except KeyError as e:
            logger.error(f"Secret key error: {e}")
            raise
    
    def put_secret(self, path: str, data: Dict[str, Any]) -> bool:
        """
        Store secret in Vault KV store.
        
        Args:
            path: Secret path
            data: Secret data dictionary
            
        Returns:
            True if successful
        """
        try:
            # Use KV v2 API format
            api_path = f"v1/secret/data/{path}"
            
            payload = {"data": data}
            
            response = self.session.post(
                f"{self.vault_addr}/{api_path}",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Successfully stored secret at '{path}'")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to store secret '{path}': {e}")
            return False
    
    def health_check(self) -> bool:
        """Check Vault server health and authentication."""
        try:
            # Check server health
            response = self.session.get(
                f"{self.vault_addr}/v1/sys/health",
                timeout=5
            )
            
            if response.status_code not in [200, 429, 472, 473]:
                return False
            
            # Check token validity
            response = self.session.get(
                f"{self.vault_addr}/v1/auth/token/lookup-self",
                timeout=5
            )
            response.raise_for_status()
            
            return True
            
        except requests.RequestException:
            return False

def create_vault_client() -> Optional[VaultClient]:
    """
    Factory function to create Vault client with error handling.
    
    Returns:
        VaultClient instance or None if Vault is not configured
    """
    try:
        if not os.getenv("VAULT_ADDR"):
            logger.warning("VAULT_ADDR not configured, skipping Vault integration")
            return None
        
        client = VaultClient()
        
        if not client.health_check():
            logger.error("Vault health check failed")
            return None
        
        return client
        
    except Exception as e:
        logger.error(f"Failed to create Vault client: {e}")
        return None

def get_cosign_public_key() -> Optional[str]:
    """Get cosign public key from Vault or environment."""
    vault = create_vault_client()
    
    if vault:
        try:
            return vault.get_secret("atom/cosign", "public_key")
        except Exception as e:
            logger.warning(f"Failed to get cosign key from Vault: {e}")
    
    # Fallback to environment variable
    key_path = os.getenv("COSIGN_PUBLIC_KEY_PATH")
    if key_path and os.path.exists(key_path):
        try:
            with open(key_path, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Failed to read cosign key from file: {e}")
    
    return None

def get_database_dsn() -> Optional[str]:
    """Get database DSN from Vault or environment."""
    vault = create_vault_client()
    
    if vault:
        try:
            return vault.get_secret("atom/database", "dsn")
        except Exception as e:
            logger.warning(f"Failed to get database DSN from Vault: {e}")
    
    # Fallback to environment variable
    return os.getenv("POSTGRES_DSN")

def get_s3_credentials() -> Optional[Dict[str, str]]:
    """Get S3 credentials from Vault or environment."""
    vault = create_vault_client()
    
    if vault:
        try:
            creds = vault.get_secret("atom/s3")
            return {
                "access_key": creds.get("access_key"),
                "secret_key": creds.get("secret_key"),
                "bucket": creds.get("bucket"),
                "endpoint": creds.get("endpoint")
            }
        except Exception as e:
            logger.warning(f"Failed to get S3 credentials from Vault: {e}")
    
    # Fallback to environment variables
    return {
        "access_key": os.getenv("S3_ACCESS_KEY"),
        "secret_key": os.getenv("S3_SECRET_KEY"),
        "bucket": os.getenv("S3_BUCKET"),
        "endpoint": os.getenv("S3_ENDPOINT")
    }