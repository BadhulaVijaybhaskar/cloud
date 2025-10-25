#!/usr/bin/env python3
"""
Tests for NeuralOps Insight Engine
"""

import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock
import numpy as np

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import InsightEngine, AnalyzeRequest

class TestInsightEngine:
    """Test cases for InsightEngine."""
    
    def setup_method(self):
        """Setup test environment."""
        self.engine = InsightEngine()
        self.engine.db_path = ":memory:"  # Use in-memory database for tests
        self.engine._init_db()
    
    def test_init_db(self):
        """Test database initialization."""
        # Database should be initialized without errors
        assert os.path.exists(self.engine.db_path) or self.engine.db_path == ":memory:"
    
    def test_detect_anomaly_normal_data(self):
        """Test anomaly detection with normal data."""
        normal_data = [100, 102, 98, 101, 99, 103, 97, 100]
        score, method, hint = self.engine._detect_anomaly(normal_data)
        
        assert score <= 0.5  # Should be low score for normal data
        assert method in ["zscore", "ewma", "normal"]
        assert isinstance(hint, str)
    
    def test_detect_anomaly_anomalous_data(self):
        """Test anomaly detection with anomalous data."""
        anomalous_data = [100, 102, 98, 101, 500, 103, 97, 100]  # 500 is anomaly
        score, method, hint = self.engine._detect_anomaly(anomalous_data)
        
        assert score > 0.5  # Should be high score for anomalous data
        assert method in ["zscore", "ewma"]
        assert "detected" in hint.lower()
    
    def test_detect_anomaly_insufficient_data(self):
        """Test anomaly detection with insufficient data."""
        insufficient_data = [100, 102]
        score, method, hint = self.engine._detect_anomaly(insufficient_data)
        
        assert score == 0.0
        assert method == "insufficient_data"
        assert "not enough" in hint.lower()
    
    def test_calculate_ewma(self):
        """Test EWMA calculation."""
        data = np.array([100, 110, 105, 115, 108])
        ewma = self.engine._calculate_ewma(data, alpha=0.3)
        
        assert isinstance(ewma, float)
        assert ewma > 0
    
    def test_generate_synthetic_data(self):
        """Test synthetic data generation."""
        data = self.engine._generate_synthetic_data()
        
        assert len(data) == 30  # Should generate 30 data points
        assert all(isinstance(x, float) for x in data)
        assert any(x > 150 for x in data)  # Should have some anomalous values
    
    def test_store_signal(self):
        """Test signal storage."""
        self.engine.store_signal(
            signal_type="test_anomaly",
            severity="warning",
            query="test_query",
            score=0.75,
            method="zscore",
            hint="Test anomaly detected",
            labels={"service": "test"}
        )
        
        # Verify signal was stored
        import sqlite3
        with sqlite3.connect(self.engine.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM insight_signals")
            count = cursor.fetchone()[0]
            assert count == 1
    
    @pytest.mark.asyncio
    async def test_analyze_metric_with_synthetic_data(self):
        """Test metric analysis with synthetic data."""
        request = AnalyzeRequest(
            query="test_metric",
            lookback="5m",
            labels={"service": "test"}
        )
        
        with patch.object(self.engine, '_is_prometheus_available', return_value=False):
            result = await self.engine.analyze_metric(request)
        
        assert isinstance(result.score, float)
        assert 0.0 <= result.score <= 1.0
        assert result.method in ["zscore", "ewma", "normal", "no_data"]
        assert isinstance(result.hint, str)
        assert result.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_analyze_metric_no_data(self):
        """Test metric analysis with no data."""
        request = AnalyzeRequest(query="nonexistent_metric")
        
        with patch.object(self.engine, '_query_prometheus', return_value=[]):
            result = await self.engine.analyze_metric(request)
        
        assert result.score == 0.0
        assert result.method == "no_data"
        assert "no data" in result.hint.lower()
    
    def test_is_prometheus_available_false(self):
        """Test Prometheus availability check when not available."""
        with patch('requests.get', side_effect=Exception("Connection failed")):
            available = self.engine._is_prometheus_available()
            assert available is False
    
    def test_is_prometheus_available_true(self):
        """Test Prometheus availability check when available."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        with patch('requests.get', return_value=mock_response):
            available = self.engine._is_prometheus_available()
            assert available is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])