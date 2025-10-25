"""
ATOM SDK - Python Client Library
Provides easy access to ATOM Cloud marketplace and services
"""
import requests
import json
from typing import Dict, List, Optional

class AtomClient:
    def __init__(self, base_url: str = "http://localhost:8050", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def publish_wpk(self, wpk_data: Dict, signature: str = None) -> Dict:
        """Publish a workflow package to the marketplace"""
        if not signature:
            signature = f"sim-sig-{hash(str(wpk_data))}"
        
        payload = {
            "name": wpk_data.get("name", "unnamed-wpk"),
            "version": wpk_data.get("version", "1.0.0"),
            "content": wpk_data,
            "signature": signature
        }
        
        try:
            response = self.session.post(f"{self.base_url}/wpk/upload", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}
    
    def list_marketplace(self, status: Optional[str] = None) -> Dict:
        """List available workflows in marketplace"""
        params = {"status": status} if status else {}
        
        try:
            response = self.session.get(f"{self.base_url}/wpk/list", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "wpks": [], "count": 0}
    
    def approve(self, wpk_id: str, reason: str = "Approved via SDK") -> Dict:
        """Approve a workflow package"""
        payload = {"status": "approved", "reason": reason}
        
        try:
            response = self.session.post(f"{self.base_url}/wpk/review/{wpk_id}", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}
    
    def reject(self, wpk_id: str, reason: str = "Rejected via SDK") -> Dict:
        """Reject a workflow package"""
        payload = {"status": "rejected", "reason": reason}
        
        try:
            response = self.session.post(f"{self.base_url}/wpk/review/{wpk_id}", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}
    
    def health(self) -> Dict:
        """Check service health"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "unhealthy"}

# Convenience functions
def create_client(base_url: str = "http://localhost:8050", api_key: str = None) -> AtomClient:
    """Create a new ATOM client instance"""
    return AtomClient(base_url, api_key)

__version__ = "1.0.0"
__all__ = ["AtomClient", "create_client"]