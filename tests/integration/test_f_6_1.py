import pytest
import requests
import os

BASE_URL = "http://localhost:8001"

def test_schema_tables_endpoint():
    """Test schema tables endpoint returns valid data"""
    response = requests.get(f"{BASE_URL}/api/data/schema/tables")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    if data:
        table = data[0]
        assert "name" in table
        assert "columns" in table
        assert "rows" in table
        assert "type" in table

def test_schema_relations_endpoint():
    """Test schema relations endpoint returns foreign keys"""
    response = requests.get(f"{BASE_URL}/api/data/schema/relations")
    assert response.status_code == 200
    
    data = response.json()
    assert "foreign_keys" in data
    assert isinstance(data["foreign_keys"], list)

def test_schema_analyze_endpoint():
    """Test schema analyze endpoint for table structure"""
    response = requests.post(f"{BASE_URL}/api/data/schema/analyze?table_name=users")
    assert response.status_code == 200
    
    data = response.json()
    assert "table" in data
    assert "columns" in data
    assert isinstance(data["columns"], list)

def test_health_check():
    """Test service health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"