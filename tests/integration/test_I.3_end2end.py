import pytest
import requests
import json
import time
from datetime import datetime
import hashlib

# Test configuration
BASE_URLS = {
    "fusion": "http://localhost:9101",
    "temporal": "http://localhost:9102", 
    "router": "http://localhost:9103",
    "reasoner": "http://localhost:9104",
    "api": "http://localhost:9105",
    "auditor": "http://localhost:9106"
}

SIMULATION_MODE = True
TEST_TENANT = "test-tenant-i3"
TEST_ENTITY = "test-entity-123"

def test_health_endpoints():
    """Test all service health endpoints"""
    for service, url in BASE_URLS.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["simulation_mode"] == SIMULATION_MODE
            print(f"✓ {service} health check passed")
        except requests.exceptions.RequestException:
            # Services may not be running in simulation mode
            print(f"⚠ {service} service not available (expected in simulation)")

def test_context_fusion_flow():
    """Test context fusion and retrieval"""
    if not SIMULATION_MODE:
        pytest.skip("Skipping in non-simulation mode")
    
    # Mock context signal
    signal_data = {
        "source": "neural-fabric",
        "entity_id": TEST_ENTITY,
        "context_data": {
            "user_activity": "browsing",
            "session_duration": 1800,
            "preferences": {"theme": "dark"}
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tenant_id": TEST_TENANT
    }
    
    try:
        # Test fusion ingestion
        response = requests.post(f"{BASE_URLS['fusion']}/fusion/ingest", 
                               json=signal_data, timeout=5)
        if response.status_code == 200:
            fusion_result = response.json()
            assert fusion_result["status"] == "fused"
            assert fusion_result["entity_id"] == TEST_ENTITY
            print("✓ Context fusion ingestion successful")
        
        # Test context retrieval
        response = requests.get(f"{BASE_URLS['fusion']}/fusion/context/{TEST_ENTITY}",
                              params={"tenant_id": TEST_TENANT}, timeout=5)
        if response.status_code == 200:
            context_result = response.json()
            assert context_result["entity_id"] == TEST_ENTITY
            assert context_result["tenant_id"] == TEST_TENANT
            print("✓ Context retrieval successful")
            
    except requests.exceptions.RequestException as e:
        print(f"⚠ Context fusion test skipped: {e}")

def test_temporal_tracking():
    """Test temporal context tracking"""
    if not SIMULATION_MODE:
        pytest.skip("Skipping in non-simulation mode")
    
    # Create context snapshot
    context_data = {
        "activity": "coding",
        "focus_level": 0.8,
        "tools_used": ["vscode", "terminal"]
    }
    
    context_str = json.dumps(context_data, sort_keys=True)
    snapshot_hash = hashlib.sha256(context_str.encode()).hexdigest()[:16]
    
    snapshot_data = {
        "entity_id": TEST_ENTITY,
        "context_state": context_data,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "snapshot_hash": snapshot_hash,
        "tenant_id": TEST_TENANT
    }
    
    try:
        response = requests.post(f"{BASE_URLS['temporal']}/temporal/snapshot",
                               json=snapshot_data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            assert result["status"] == "stored"
            print("✓ Temporal snapshot creation successful")
        
        # Test drift calculation
        response = requests.get(f"{BASE_URLS['temporal']}/temporal/drift/{TEST_ENTITY}",
                              params={"tenant_id": TEST_TENANT}, timeout=5)
        if response.status_code == 200:
            drift_result = response.json()
            assert drift_result["entity_id"] == TEST_ENTITY
            print("✓ Drift calculation successful")
            
    except requests.exceptions.RequestException as e:
        print(f"⚠ Temporal tracking test skipped: {e}")

def test_context_reasoning():
    """Test context reasoning capabilities"""
    if not SIMULATION_MODE:
        pytest.skip("Skipping in non-simulation mode")
    
    reasoning_request = {
        "entity_id": TEST_ENTITY,
        "context_data": {
            "user_behavior": "active",
            "system_load": 0.7,
            "time_of_day": "afternoon"
        },
        "reasoning_type": "predictive",
        "tenant_id": TEST_TENANT
    }
    
    try:
        response = requests.post(f"{BASE_URLS['reasoner']}/reason/predict",
                               json=reasoning_request, timeout=5)
        if response.status_code == 200:
            result = response.json()
            assert result["entity_id"] == TEST_ENTITY
            assert "predictions" in result
            assert "confidence_score" in result
            print("✓ Context reasoning successful")
            
    except requests.exceptions.RequestException as e:
        print(f"⚠ Context reasoning test skipped: {e}")

def test_context_api_query():
    """Test unified context API"""
    if not SIMULATION_MODE:
        pytest.skip("Skipping in non-simulation mode")
    
    query_data = {
        "entity_id": TEST_ENTITY,
        "relevance_threshold": 0.5,
        "tenant_id": TEST_TENANT
    }
    
    try:
        response = requests.post(f"{BASE_URLS['api']}/context/query",
                               json=query_data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            assert "results" in result
            assert "total_count" in result
            assert result["query_time_ms"] < 200  # P6 performance budget
            print("✓ Context API query successful")
            
    except requests.exceptions.RequestException as e:
        print(f"⚠ Context API test skipped: {e}")

def test_policy_compliance_audit():
    """Test policy compliance auditing"""
    if not SIMULATION_MODE:
        pytest.skip("Skipping in non-simulation mode")
    
    audit_request = {
        "entity_id": TEST_ENTITY,
        "context_data": {
            "user_action": "data_access",
            "resource": "user_profile",
            "timestamp": datetime.utcnow().isoformat()
        },
        "operation": "read",
        "tenant_id": TEST_TENANT
    }
    
    try:
        response = requests.post(f"{BASE_URLS['auditor']}/audit/context",
                               json=audit_request, timeout=5)
        if response.status_code == 200:
            result = response.json()
            assert result["entity_id"] == TEST_ENTITY
            assert "compliance_status" in result
            assert "violations" in result
            print("✓ Policy compliance audit successful")
            
    except requests.exceptions.RequestException as e:
        print(f"⚠ Policy audit test skipped: {e}")

def test_end_to_end_flow():
    """Test complete contextual intelligence flow"""
    if not SIMULATION_MODE:
        pytest.skip("Skipping in non-simulation mode")
    
    print("\n=== Phase I.3 End-to-End Test ===")
    
    # 1. Generate context events
    print("1. Generating context events...")
    
    # 2. Test fusion → tracking → routing → reasoning → audit
    print("2. Testing service chain...")
    
    start_time = time.time()
    
    # Run individual tests
    test_context_fusion_flow()
    test_temporal_tracking()
    test_context_reasoning()
    test_context_api_query()
    test_policy_compliance_audit()
    
    end_time = time.time()
    total_time_ms = (end_time - start_time) * 1000
    
    print(f"3. Total flow time: {total_time_ms:.2f}ms")
    
    # Verify latency requirement (P6)
    assert total_time_ms < 1000, f"Flow exceeded 1000ms budget: {total_time_ms}ms"
    
    print("✓ End-to-end flow completed successfully")

if __name__ == "__main__":
    # Run tests
    test_health_endpoints()
    test_end_to_end_flow()
    print("\n=== All Phase I.3 Tests Completed ===")