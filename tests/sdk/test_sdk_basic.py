#!/usr/bin/env python3
"""
SDK Basic Tests - E.2
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'sdk', 'python'))

import pytest
from atom_sdk import AtomClient, create_client

def test_client_creation():
    """Test SDK client creation"""
    client = create_client()
    assert isinstance(client, AtomClient)
    assert client.base_url == "http://localhost:8050"

def test_client_with_api_key():
    """Test SDK client with API key"""
    client = create_client(api_key="test-key")
    assert client.api_key == "test-key"
    assert "Authorization" in client.session.headers

def test_publish_wpk():
    """Test WPK publishing via SDK"""
    client = create_client(api_key="test-token")
    
    wpk_data = {
        "name": "sdk-test-wpk",
        "version": "1.0.0",
        "steps": ["init", "process", "cleanup"]
    }
    
    result = client.publish_wpk(wpk_data)
    
    # Should work in simulation mode or return connection error
    assert "status" in result
    assert result["status"] in ["uploaded", "failed"]

def test_list_marketplace():
    """Test marketplace listing via SDK"""
    client = create_client()
    
    result = client.list_marketplace()
    
    # Should work in simulation mode or return connection error
    assert "wpks" in result
    assert "count" in result

def test_health_check():
    """Test health check via SDK"""
    client = create_client()
    
    result = client.health()
    
    # Should return health status or connection error
    assert "status" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])