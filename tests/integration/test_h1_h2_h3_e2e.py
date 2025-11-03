#!/usr/bin/env python3
"""
H1-H3 Integration End-to-End Test
Tests complete workflow: AI-Proxy -> Workflow-Registry -> LangGraph execution
"""

import pytest
import requests
import json
import time
import os
from typing import Dict, Any

# Test Configuration
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "http://localhost:8081")
LANGGRAPH_URL = os.getenv("LANGGRAPH_URL", "http://localhost:8080")
WORKFLOW_REGISTRY_URL = os.getenv("WORKFLOW_REGISTRY_URL", "http://localhost:8084")

# Test Data
TEST_GRAPH_DEFINITION = {
    "id": "test-graph-1",
    "name": "Test Graph",
    "nodes": [
        {"id": "start", "type": "input", "config": {}},
        {"id": "process", "type": "transform", "config": {"operation": "uppercase"}},
        {"id": "end", "type": "output", "config": {}}
    ],
    "edges": [
        {"from": "start", "to": "process"},
        {"from": "process", "to": "end"}
    ]
}

TEST_WORKFLOW_DEFINITION = {
    "id": "test-workflow-1",
    "name": "Test Workflow",
    "description": "End-to-end test workflow",
    "graph_definition": TEST_GRAPH_DEFINITION,
    "tenant_id": "test-tenant",
    "triggers": [{"type": "api", "endpoint": "/trigger"}]
}

class TestH1H2H3Integration:
    """Integration tests for H1-H3 components"""
    
    def setup_method(self):
        """Setup test environment"""
        self.headers = {
            "Authorization": "Bearer test-token",
            "Content-Type": "application/json"
        }
        self.tenant_id = "test-tenant"
    
    def test_service_health_checks(self):
        """Test that all services are healthy"""
        if SIMULATION_MODE:
            pytest.skip("Simulation mode - skipping connectivity tests")
        
        # Test LangGraph health
        response = requests.get(f"{LANGGRAPH_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
        # Test AI-Proxy health
        response = requests.get(f"{AI_PROXY_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
        # Test Workflow Registry health
        response = requests.get(f"{WORKFLOW_REGISTRY_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_langgraph_direct_execution(self):
        """Test direct LangGraph execution"""
        # Create graph
        response = requests.post(
            f"{LANGGRAPH_URL}/v1/graphs",
            json=TEST_GRAPH_DEFINITION,
            headers=self.headers
        )
        assert response.status_code == 200
        
        # Execute graph
        execution_request = {
            "graph_id": "test-graph-1",
            "inputs": {"text": "hello world"},
            "tenant_id": self.tenant_id
        }
        
        response = requests.post(
            f"{LANGGRAPH_URL}/v1/execute",
            json=execution_request,
            headers=self.headers
        )
        assert response.status_code == 200
        
        execution_data = response.json()
        assert "execution_id" in execution_data
        assert execution_data["status"] in ["queued", "running"]
        
        # Check execution status
        execution_id = execution_data["execution_id"]
        response = requests.get(
            f"{LANGGRAPH_URL}/v1/executions/{execution_id}",
            params={"tenant_id": self.tenant_id},
            headers=self.headers
        )
        assert response.status_code == 200
    
    def test_workflow_registry_operations(self):
        """Test workflow registry CRUD operations"""
        # Register workflow
        response = requests.post(
            f"{WORKFLOW_REGISTRY_URL}/v1/workflows",
            json=TEST_WORKFLOW_DEFINITION,
            headers=self.headers
        )
        assert response.status_code == 200
        
        # List workflows
        response = requests.get(
            f"{WORKFLOW_REGISTRY_URL}/v1/workflows",
            params={"tenant_id": self.tenant_id},
            headers=self.headers
        )
        assert response.status_code == 200
        
        workflows_data = response.json()
        assert "workflows" in workflows_data
        
        # Get specific workflow
        response = requests.get(
            f"{WORKFLOW_REGISTRY_URL}/v1/workflows/test-workflow-1",
            params={"tenant_id": self.tenant_id},
            headers=self.headers
        )
        assert response.status_code == 200
    
    def test_ai_proxy_graph_execution(self):
        """Test graph execution through AI-Proxy"""
        execution_request = {
            "graph_id": "test-graph-1",
            "inputs": {"text": "hello via proxy"},
            "execution_mode": "async"
        }
        
        response = requests.post(
            f"{AI_PROXY_URL}/v1/graphs/execute",
            json=execution_request,
            headers=self.headers
        )
        assert response.status_code == 200
        
        execution_data = response.json()
        assert "execution_id" in execution_data
        
        # Check status through proxy
        execution_id = execution_data["execution_id"]
        response = requests.get(
            f"{AI_PROXY_URL}/v1/status/{execution_id}",
            headers=self.headers
        )
        assert response.status_code == 200
    
    def test_ai_proxy_workflow_trigger(self):
        """Test workflow triggering through AI-Proxy"""
        trigger_request = {
            "workflow_id": "test-workflow-1",
            "inputs": {"text": "hello workflow"},
            "trigger_type": "api"
        }
        
        response = requests.post(
            f"{AI_PROXY_URL}/v1/workflows/trigger",
            json=trigger_request,
            headers=self.headers
        )
        assert response.status_code == 200
        
        trigger_data = response.json()
        assert "workflow_execution_id" in trigger_data or "execution_id" in trigger_data
    
    def test_end_to_end_workflow_execution(self):
        """Test complete end-to-end workflow execution"""
        # 1. Register workflow via Workflow Registry
        response = requests.post(
            f"{WORKFLOW_REGISTRY_URL}/v1/workflows",
            json=TEST_WORKFLOW_DEFINITION,
            headers=self.headers
        )
        assert response.status_code == 200
        
        # 2. Trigger workflow via AI-Proxy
        trigger_request = {
            "workflow_id": "test-workflow-1",
            "inputs": {"text": "end-to-end test"},
            "trigger_type": "api"
        }
        
        response = requests.post(
            f"{AI_PROXY_URL}/v1/workflows/trigger",
            json=trigger_request,
            headers=self.headers
        )
        assert response.status_code == 200
        
        trigger_data = response.json()
        execution_id = trigger_data.get("workflow_execution_id") or trigger_data.get("execution_id")
        assert execution_id is not None
        
        # 3. Monitor execution status
        max_attempts = 10
        for attempt in range(max_attempts):
            response = requests.get(
                f"{AI_PROXY_URL}/v1/status/{execution_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                status_data = response.json()
                if status_data.get("status") in ["completed", "failed"]:
                    break
            
            time.sleep(1)
        
        # Verify final status
        assert response.status_code == 200
        final_status = response.json()
        
        if SIMULATION_MODE:
            assert final_status.get("status") == "completed"
        else:
            assert final_status.get("status") in ["completed", "running"]
    
    def test_metrics_endpoints(self):
        """Test that all services expose metrics"""
        services = [
            (LANGGRAPH_URL, "langgraph"),
            (AI_PROXY_URL, "ai-proxy"),
            (WORKFLOW_REGISTRY_URL, "workflow-registry")
        ]
        
        for service_url, service_name in services:
            response = requests.get(f"{service_url}/metrics")
            assert response.status_code == 200
            
            metrics_text = response.text
            assert f"# HELP" in metrics_text
            assert f"# TYPE" in metrics_text

if __name__ == "__main__":
    pytest.main([__file__, "-v"])