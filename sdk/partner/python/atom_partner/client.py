"""
Atom Partner SDK Client
"""
import os
import requests
from typing import Dict, Any, Optional

class AtomPartnerClient:
    """
    Main client for interacting with Atom Partner APIs.
    
    Args:
        base_url: Base URL for the partner API
        token: Authentication token (optional)
    """
    
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """Initialize the client with base URL and optional token."""
        self.base_url = base_url or os.getenv("ATOM_PARTNER_BASE", "http://localhost:8200")
        self.token = token
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def register_partner(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new partner.
        
        Args:
            payload: Partner registration data
            
        Returns:
            Registration response
        """
        response = self.session.post(f"{self.base_url}/v1/partners", json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    
    def get_partner(self, partner_id: str) -> Dict[str, Any]:
        """
        Get partner details by ID.
        
        Args:
            partner_id: Partner identifier
            
        Returns:
            Partner details
        """
        response = self.session.get(f"{self.base_url}/v1/partners/{partner_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    
    def publish_package(self, package_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish a package to the marketplace.
        
        Args:
            package_data: Package metadata and content
            
        Returns:
            Publication response with job ID
        """
        response = self.session.post(f"{self.base_url}/v1/publish", json=package_data, timeout=10)
        response.raise_for_status()
        return response.json()
