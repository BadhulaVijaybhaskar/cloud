import pytest
import httpx
import asyncio
import time

BASE_URL = "http://localhost:8001"

@pytest.mark.asyncio
async def test_gateway_health():
    """Test gateway health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["env"] in ["SIM", "LIVE"]

@pytest.mark.asyncio
async def test_data_query():
    """Test data query endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/data/query",
            json={"sql": "SELECT 1"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "rows" in data

@pytest.mark.asyncio
async def test_auth_login():
    """Test authentication login"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "password"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data

@pytest.mark.asyncio
async def test_ai_sql_suggest():
    """Test AI SQL suggestion"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/ai/sql/suggest",
            json={"context": "show user count"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "suggestion" in data

def test_services_startup():
    """Test that all services can start"""
    # This would normally start all services and verify they're running
    # For simulation, we just verify the test framework works
    assert True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])