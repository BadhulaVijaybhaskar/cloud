#!/usr/bin/env python3
"""
Tests for Performance Profiler - Phase C.2
"""

import pytest
import asyncio
import tempfile
import os
import sys
import aiohttp
from aiohttp import web
import threading
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from agent import PerformanceProfiler, BenchmarkResult

class TestPerformanceProfiler:
    """Test cases for performance profiler"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.profiler = PerformanceProfiler(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except (PermissionError, OSError):
                pass
    
    def test_profiler_initialization(self):
        """Test profiler initializes correctly"""
        assert self.profiler.db_path == self.temp_db.name
        assert "registry" in self.profiler.services
        assert "runtime" in self.profiler.services
        assert "insight" in self.profiler.services
    
    def test_store_result(self):
        """Test storing benchmark results"""
        result = BenchmarkResult(
            service="test-service",
            endpoint="/test",
            p50_ms=100.0,
            p95_ms=200.0,
            p99_ms=300.0,
            throughput=50.0,
            error_rate=1.0,
            test_duration_sec=30,
            concurrent_users=10
        )
        
        result_id = self.profiler.store_result(result)
        assert result_id is not None
        
        # Verify stored
        metrics = self.profiler.get_latest_metrics(limit=1)
        assert len(metrics) == 1
        assert metrics[0]["service"] == "test-service"
        assert metrics[0]["p95_ms"] == 200.0
    
    def test_performance_budget_check(self):
        """Test P-6 performance budget validation"""
        # Within budget
        good_result = BenchmarkResult(
            service="fast-service", endpoint="/test", p50_ms=100, p95_ms=500, p99_ms=600,
            throughput=100, error_rate=0, test_duration_sec=30, concurrent_users=10
        )
        assert self.profiler.check_performance_budget(good_result) == True
        
        # Budget violation
        slow_result = BenchmarkResult(
            service="slow-service", endpoint="/test", p50_ms=600, p95_ms=900, p99_ms=1200,
            throughput=10, error_rate=5, test_duration_sec=30, concurrent_users=10
        )
        assert self.profiler.check_performance_budget(slow_result) == False
    
    def test_get_latest_metrics(self):
        """Test retrieving latest metrics"""
        # Store multiple results
        for i in range(3):
            result = BenchmarkResult(
                service=f"service-{i}", endpoint="/test", p50_ms=100+i*10, p95_ms=200+i*20, 
                p99_ms=300+i*30, throughput=50-i*5, error_rate=i, 
                test_duration_sec=30, concurrent_users=10
            )
            self.profiler.store_result(result)
        
        metrics = self.profiler.get_latest_metrics(limit=2)
        assert len(metrics) == 2
        # Verify we get the expected number of results
        services = [m["service"] for m in metrics]
        assert len(set(services)) <= 2  # At most 2 different services

class TestBenchmarkIntegration:
    """Integration tests with mock HTTP server"""
    
    def setup_method(self):
        """Setup mock HTTP server"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.profiler = PerformanceProfiler(db_path=self.temp_db.name)
        
        # Start mock server
        self.server_port = 18999
        self.server_thread = None
        self.start_mock_server()
    
    def teardown_method(self):
        """Cleanup"""
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except (PermissionError, OSError):
                pass
    
    def start_mock_server(self):
        """Start mock HTTP server for testing"""
        async def healthz_handler(request):
            # Simulate some processing time
            await asyncio.sleep(0.01)  # 10ms
            return web.json_response({"status": "healthy"})
        
        async def slow_handler(request):
            # Simulate slow endpoint
            await asyncio.sleep(0.1)  # 100ms
            return web.json_response({"status": "slow"})
        
        app = web.Application()
        app.router.add_get('/healthz', healthz_handler)
        app.router.add_get('/slow', slow_handler)
        
        def run_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            runner = web.AppRunner(app)
            loop.run_until_complete(runner.setup())
            site = web.TCPSite(runner, 'localhost', self.server_port)
            loop.run_until_complete(site.start())
            loop.run_forever()
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        time.sleep(0.5)  # Wait for server to start
    
    @pytest.mark.asyncio
    async def test_benchmark_endpoint_success(self):
        """Test successful endpoint benchmarking"""
        result = await self.profiler.benchmark_endpoint(
            service="test-service",
            base_url=f"http://localhost:{self.server_port}",
            endpoint="/healthz",
            duration=2,  # Short test
            concurrent=2
        )
        
        assert result.service == "test-service"
        assert result.endpoint == "/healthz"
        assert result.p95_ms > 0
        assert result.throughput > 0
        assert result.error_rate < 50  # Should be mostly successful
    
    @pytest.mark.asyncio
    async def test_benchmark_endpoint_timeout(self):
        """Test benchmarking unreachable endpoint"""
        result = await self.profiler.benchmark_endpoint(
            service="unreachable",
            base_url="http://localhost:19999",  # Non-existent port
            endpoint="/test",
            duration=1,
            concurrent=1
        )
        
        assert result.service == "unreachable"
        assert result.p95_ms == 999999  # Error indicator
        assert result.throughput == 0
        assert result.error_rate == 100

class TestPolicyCompliance:
    """Test P1-P6 policy compliance"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.profiler = PerformanceProfiler(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Cleanup"""
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except (PermissionError, OSError):
                pass
    
    def test_p4_observability_metrics(self):
        """Test P-4: Metrics are properly emitted"""
        result = BenchmarkResult(
            service="metrics-test", endpoint="/test", p50_ms=100, p95_ms=200, p99_ms=300,
            throughput=50, error_rate=2, test_duration_sec=30, concurrent_users=10
        )
        
        # Store and verify metrics are captured
        result_id = self.profiler.store_result(result)
        metrics = self.profiler.get_latest_metrics(limit=1)
        
        assert len(metrics) == 1
        assert "p95_ms" in metrics[0]
        assert "throughput" in metrics[0]
        assert "error_rate" in metrics[0]
    
    def test_p6_performance_budget_enforcement(self):
        """Test P-6: Performance budget enforcement (p95 < 800ms)"""
        # Test budget compliance
        fast_result = BenchmarkResult(
            service="fast", endpoint="/test", p50_ms=100, p95_ms=500, p99_ms=600,
            throughput=100, error_rate=0, test_duration_sec=30, concurrent_users=10
        )
        assert self.profiler.check_performance_budget(fast_result) == True
        
        # Test budget violation
        slow_result = BenchmarkResult(
            service="slow", endpoint="/test", p50_ms=600, p95_ms=1000, p99_ms=1500,
            throughput=10, error_rate=5, test_duration_sec=30, concurrent_users=10
        )
        assert self.profiler.check_performance_budget(slow_result) == False
        
        # Boundary case
        boundary_result = BenchmarkResult(
            service="boundary", endpoint="/test", p50_ms=400, p95_ms=800.0, p99_ms=900,
            throughput=50, error_rate=1, test_duration_sec=30, concurrent_users=10
        )
        assert self.profiler.check_performance_budget(boundary_result) == True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])