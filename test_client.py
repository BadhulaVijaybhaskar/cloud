#!/usr/bin/env python3
"""
Naksha Cloud Integration Test Client
Tests services when they are running
"""

import requests
import json
import time
from datetime import datetime

def test_service_health(service_name, url, expected_status=200):
    """Test if a service is healthy"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            return True, f"[OK] {service_name}: HTTP {response.status_code}"
        else:
            return False, f"[FAIL] {service_name}: HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"[FAIL] {service_name}: {str(e)}"

def test_langgraph_job():
    """Test LangGraph job submission"""
    try:
        job_data = {
            "graph_name": "sample_rag",
            "input_data": {"query": "integration test"}
        }
        response = requests.post(
            "http://localhost:8081/v1/jobs",
            json=job_data,
            timeout=10
        )
        if response.status_code == 200:
            return True, f"[OK] LangGraph Job: {response.json()}"
        else:
            return False, f"[FAIL] LangGraph Job: HTTP {response.status_code}"
    except Exception as e:
        return False, f"[FAIL] LangGraph Job: {str(e)}"

def main():
    print("=== Naksha Cloud Integration Test Client ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Test services
    services = [
        ("Admin UI", "http://localhost:3000"),
        ("Auth Service", "http://localhost:9999/health"),
        ("Realtime Service", "http://localhost:4000/health"),
        ("Hasura GraphQL", "http://localhost:8080/healthz"),
        ("LangGraph", "http://localhost:8081/healthz"),
        ("Vector Service", "http://localhost:8082/healthz"),
    ]
    
    results = []
    for service_name, url in services:
        success, message = test_service_health(service_name, url)
        results.append((service_name, success, message))
        print(message)
    
    print()
    
    # Test LangGraph functionality if available
    if any(result[0] == "LangGraph" and result[1] for result in results):
        print("Testing LangGraph functionality...")
        success, message = test_langgraph_job()
        print(message)
    
    print()
    print("=== Test Summary ===")
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"Services Passed: {passed}/{total}")
    
    if passed == total:
        print("SUCCESS: All services are healthy!")
        return 0
    else:
        print("WARNING: Some services need attention")
        return 1

if __name__ == "__main__":
    exit(main())