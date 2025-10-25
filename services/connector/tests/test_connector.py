#!/usr/bin/env python3
"""
Tests for BYOC Connector
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agent import BYOCConnector, ConnectorConfig, ExecutionRequest
from auth import VaultAuth
from metrics import MetricsStreamer
from executor import WPKExecutor

class TestBYOCConnector:
    """Test cases for BYOC Connector."""
    
    def setup_method(self):
        """Setup test environment."""
        self.config = ConnectorConfig()
        self.config.simulate = True
        self.connector = BYOCConnector(self.config)
    
    @pytest.mark.asyncio
    async def test_cluster_registration(self):
        """Test cluster registration with control plane."""
        result = await self.connector.register_cluster()
        
        assert result is True
        assert self.connector.registered is True
    
    @pytest.mark.asyncio
    async def test_wpk_execution(self):
        """Test WPK execution workflow."""
        request = ExecutionRequest(
            playbook_id="test-playbook",
            signature="mock-signature-12345",
            payload={"manifest": {"apiVersion": "v1", "kind": "Pod"}},
            orchestration_id="test-orch-123"
        )
        
        result = await self.connector.execute_wpk(request)
        
        assert result["status"] == "success"
        assert result["cluster_id"] == self.config.cluster_id
        assert "execution_id" in result

class TestVaultAuth:
    """Test cases for Vault authentication."""
    
    def setup_method(self):
        """Setup test environment."""
        self.auth = VaultAuth("", simulate=True)
    
    @pytest.mark.asyncio
    async def test_get_token_simulation(self):
        """Test token retrieval in simulation mode."""
        token = await self.auth.get_token()
        
        assert token == "mock-vault-token-12345"
    
    @pytest.mark.asyncio
    async def test_get_secret_simulation(self):
        """Test secret retrieval in simulation mode."""
        secret = await self.auth.get_secret("secret/test")
        
        assert secret is not None
        assert "data" in secret

class TestMetricsStreamer:
    """Test cases for metrics streaming."""
    
    def setup_method(self):
        """Setup test environment."""
        self.streamer = MetricsStreamer("", "", simulate=True)
    
    @pytest.mark.asyncio
    async def test_collect_metrics_simulation(self):
        """Test metrics collection in simulation mode."""
        metrics = await self.streamer.collect_metrics()
        
        assert len(metrics) == 3
        assert all("metric" in m for m in metrics)
        assert all("value" in m for m in metrics)
    
    @pytest.mark.asyncio
    async def test_stream_metrics(self):
        """Test metrics streaming to control plane."""
        await self.streamer.stream_metrics("test-cluster")
        
        assert self.streamer.metrics_sent == 3

class TestWPKExecutor:
    """Test cases for WPK execution."""
    
    def setup_method(self):
        """Setup test environment."""
        self.executor = WPKExecutor("", simulate=True)
    
    @pytest.mark.asyncio
    async def test_signature_verification(self):
        """Test cosign signature verification."""
        result = await self.executor.verify_signature(
            "mock-signature", 
            {"test": "payload"}
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_wpk_execution(self):
        """Test WPK playbook execution."""
        result = await self.executor.execute(
            "test-playbook",
            {"manifest": {"apiVersion": "v1", "kind": "Pod"}}
        )
        
        assert result["status"] == "success"
        assert result["playbook_id"] == "test-playbook"
        assert "execution_id" in result
    
    def test_execution_summary(self):
        """Test execution summary statistics."""
        # Add some mock executions
        self.executor.executions = [
            {"status": "success"},
            {"status": "success"},
            {"status": "failed"}
        ]
        
        summary = self.executor.get_execution_summary()
        
        assert summary["total_executions"] == 3
        assert summary["successful"] == 2
        assert summary["failed"] == 1
        assert abs(summary["success_rate"] - 66.67) < 0.1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])