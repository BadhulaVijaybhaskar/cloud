import pytest
import requests
import time

BASE_URLS = {
    "data": "http://localhost:8001",
    "backup": "http://localhost:8003", 
    "migrations": "http://localhost:8004",
    "export": "http://localhost:8005"
}

def test_all_services_healthy():
    """Test all F.6 services are healthy"""
    for service, url in BASE_URLS.items():
        response = requests.get(f"{url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "ok"]

def test_schema_visualization():
    """Test schema endpoints work"""
    response = requests.get(f"{BASE_URLS['data']}/api/data/schema/tables")
    assert response.status_code == 200
    
    tables = response.json()
    assert isinstance(tables, list)
    assert len(tables) > 0

def test_crud_operations():
    """Test CRUD operations on tables"""
    # Get table data
    response = requests.get(f"{BASE_URLS['data']}/api/data/crud/tables/users/rows")
    assert response.status_code == 200
    
    data = response.json()
    assert "rows" in data
    assert "total" in data

def test_backup_operations():
    """Test backup service"""
    response = requests.get(f"{BASE_URLS['backup']}/list")
    assert response.status_code == 200
    
    data = response.json()
    assert "backups" in data

def test_migrations_service():
    """Test migrations service"""
    response = requests.get(f"{BASE_URLS['migrations']}/list")
    assert response.status_code == 200
    
    data = response.json()
    assert "migrations" in data

def test_export_service():
    """Test export service"""
    response = requests.get(f"{BASE_URLS['export']}/webhooks")
    assert response.status_code == 200
    
    data = response.json()
    assert "webhooks" in data

def test_performance_budget():
    """Test P6 performance requirements"""
    start_time = time.time()
    response = requests.get(f"{BASE_URLS['data']}/api/data/schema/tables")
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 1.0  # P6: < 1s response time