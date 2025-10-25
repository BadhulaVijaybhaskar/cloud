#!/usr/bin/env python3
"""
Vault authentication for BYOC Connector.
"""

import os
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)

class VaultAuth:
    """Handles Vault authentication for BYOC Connector."""
    
    def __init__(self, vault_addr: str, simulate: bool = False):
        self.vault_addr = vault_addr
        self.simulate = simulate
        self.token = None
    
    async def get_token(self) -> Optional[str]:
        """Get Vault token for authentication."""
        if self.simulate:
            logger.info("SIMULATION: Using mock Vault token")
            return "mock-vault-token-12345"
        
        if not self.vault_addr:
            logger.warning("VAULT_ADDR not set, using simulation mode")
            return "mock-vault-token-12345"
        
        try:
            # In production, this would use proper Vault AppRole authentication
            role_id = os.getenv("VAULT_ROLE_ID", "")
            secret_id = os.getenv("VAULT_SECRET_ID", "")
            
            if not role_id or not secret_id:
                logger.warning("Vault credentials not found, using mock token")
                return "mock-vault-token-12345"
            
            auth_data = {
                "role_id": role_id,
                "secret_id": secret_id
            }
            
            response = requests.post(
                f"{self.vault_addr}/v1/auth/approle/login",
                json=auth_data,
                timeout=10
            )
            
            if response.status_code == 200:
                auth_response = response.json()
                self.token = auth_response["auth"]["client_token"]
                logger.info("Successfully authenticated with Vault")
                return self.token
            else:
                logger.error(f"Vault authentication failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Vault authentication error: {e}")
            return None
    
    async def get_secret(self, path: str) -> Optional[dict]:
        """Retrieve secret from Vault."""
        if self.simulate:
            logger.info(f"SIMULATION: Retrieved secret from {path}")
            return {"data": {"mock_key": "mock_value"}}
        
        if not self.token:
            await self.get_token()
        
        if not self.token:
            return None
        
        try:
            response = requests.get(
                f"{self.vault_addr}/v1/{path}",
                headers={"X-Vault-Token": self.token},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to retrieve secret: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Secret retrieval error: {e}")
            return None