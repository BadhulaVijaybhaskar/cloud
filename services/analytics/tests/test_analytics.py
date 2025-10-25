#!/usr/bin/env python3
"""
Tests for Analytics Service - Phase C.4
"""

import pytest
import tempfile
import os
import sys
import json
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from server import app, analytics_service, AnalyticsService

class TestAnalyticsService:
    """Test cases for analytics service core functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.analytics = AnalyticsService(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except (PermissionError, OSError):
                pass
    
    def test_analytics_initialization(self):
        """Test analytics service initializes correctly"""
        assert self.analytics.db_path == self.temp_db.name
        
        # Check sample data was inserted
        overview = self.analytics.get_analytics_overview()
        assert len(overview) >= 1
        assert overview[0].tenant_name == "Default Tenant"
    
    def test_get_analytics_overview(self):
        """Test analytics overview generation"""
        overview = self.analytics.get_analytics_overview()
        
        assert len(overview) >= 1
        tenant_overview = overview[0]
        
        assert tenant_overview.tenant_id is not None
        assert tenant_overview.tenant_name == "Default Tenant"
        assert tenant_overview.total_workflows >= 0
        assert tenant_overview.failure_rate_percent >= 0
        assert tenant_overview.failure_rate_percent <= 100
    
    def test_get_mttr_analysis(self):
        """Test MTTR analysis calculation"""
        mttr_data = self.analytics.get_mttr_analysis()
        
        if mttr_data:  # May be empty if no failures
            mttr = mttr_data[0]
            assert mttr.tenant_id is not None
            assert mttr.total_incidents >= 0
            assert mttr.avg_mttr_minutes >= 0
            assert mttr.median_mttr_minutes >= 0
    
    def test_get_cost_analysis(self):
        """Test cost analysis calculation"""
        cost_data = self.analytics.get_cost_analysis()
        
        assert len(cost_data) >= 1
        cost = cost_data[0]
        
        assert cost.tenant_id is not None
        assert cost.workflow_execution_cost >= 0
        assert cost.monitoring_cost >= 0
        assert cost.prediction_cost >= 0
        assert cost.total_estimated_cost >= 0
    
    def test_get_usage_trends(self):
        """Test usage trends over time"""
        default_tenant = "00000000-0000-0000-0000-000000000001"
        trends = self.analytics.get_usage_trends(default_tenant, days=7)
        
        # Should have some trend data
        assert isinstance(trends, list)
        
        if trends:
            trend = trends[0]
            assert 'usage_date' in trend
            assert 'daily_workflows' in trend
            assert 'daily_failure_rate' in trend
            assert trend['daily_failure_rate'] >= 0
    
    def test_tenant_specific_queries(self):
        """Test tenant-specific data filtering"""
        default_tenant = "00000000-0000-0000-0000-000000000001"
        
        # Get overview for specific tenant
        overview = self.analytics.get_analytics_overview(default_tenant)
        assert len(overview) == 1
        assert overview[0].tenant_id == default_tenant
        
        # Get cost analysis for specific tenant
        costs = self.analytics.get_cost_analysis(default_tenant)
        assert len(costs) == 1
        assert costs[0].tenant_id == default_tenant
    
    def test_export_to_csv(self):
        """Test CSV export functionality"""
        sample_data = [
            {'name': 'test1', 'value': 100},
            {'name': 'test2', 'value': 200}
        ]
        
        csv_content = self.analytics.export_to_csv(sample_data, "test.csv")
        
        assert "name,value" in csv_content
        assert "test1,100" in csv_content
        assert "test2,200" in csv_content
    
    def test_empty_data_handling(self):
        """Test handling of empty datasets"""
        # Test with non-existent tenant
        fake_tenant = "99999999-9999-9999-9999-999999999999"
        
        overview = self.analytics.get_analytics_overview(fake_tenant)
        assert len(overview) == 0
        
        trends = self.analytics.get_usage_trends(fake_tenant)
        assert isinstance(trends, list)

class TestAnalyticsAPI:
    """Test cases for analytics API endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/healthz")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "analytics"
    
    def test_overview_report_endpoint(self):
        """Test overview report API"""
        response = self.client.get("/reports/overview")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "generated_at" in data
        
        if data["data"]:
            tenant_data = data["data"][0]
            assert "tenant_id" in tenant_data
            assert "total_workflows" in tenant_data
            assert "failure_rate_percent" in tenant_data
    
    def test_tenant_specific_report(self):
        """Test tenant-specific report endpoint"""
        default_tenant = "00000000-0000-0000-0000-000000000001"
        response = self.client.get(f"/reports/tenant/{default_tenant}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["tenant_id"] == default_tenant
        assert "overview" in data
        assert "usage_trends" in data
    
    def test_mttr_report_endpoint(self):
        """Test MTTR report API"""
        response = self.client.get("/reports/mttr")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
    
    def test_cost_report_endpoint(self):
        """Test cost report API"""
        response = self.client.get("/reports/costs")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        
        if data["data"]:
            cost_data = data["data"][0]
            assert "total_estimated_cost" in cost_data
            assert "workflow_execution_cost" in cost_data
    
    def test_trends_report_endpoint(self):
        """Test trends report API"""
        default_tenant = "00000000-0000-0000-0000-000000000001"
        response = self.client.get(f"/reports/trends/{default_tenant}?days=7")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["tenant_id"] == default_tenant
        assert data["period_days"] == 7
        assert "data" in data
    
    def test_csv_export_endpoint(self):
        """Test CSV export API"""
        response = self.client.get("/export/csv/overview")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    def test_invalid_csv_export(self):
        """Test invalid CSV export request"""
        response = self.client.get("/export/csv/invalid_type")
        assert response.status_code == 400
    
    def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint"""
        response = self.client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "analytics_reports_generated_total" in data
        assert "analytics_service_uptime_seconds" in data
    
    def test_nonexistent_tenant_report(self):
        """Test report for non-existent tenant"""
        fake_tenant = "99999999-9999-9999-9999-999999999999"
        response = self.client.get(f"/reports/tenant/{fake_tenant}")
        
        assert response.status_code == 404
    
    def test_query_parameters(self):
        """Test API query parameters"""
        default_tenant = "00000000-0000-0000-0000-000000000001"
        
        # Test tenant_id parameter
        response = self.client.get(f"/reports/overview?tenant_id={default_tenant}")
        assert response.status_code == 200
        
        data = response.json()
        if data["data"]:
            assert data["data"][0]["tenant_id"] == default_tenant
        
        # Test days parameter
        response = self.client.get(f"/reports/trends/{default_tenant}?days=14")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_days"] == 14

class TestPolicyCompliance:
    """Test P1-P6 policy compliance"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.analytics = AnalyticsService(db_path=self.temp_db.name)
        self.client = TestClient(app)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except (PermissionError, OSError):
                pass
    
    def test_p1_data_privacy(self):
        """Test P-1: No PII in analytics data"""
        overview = self.analytics.get_analytics_overview()
        
        for tenant_overview in overview:
            # Ensure no PII fields are exposed
            data_dict = tenant_overview.__dict__
            
            # Check that we only have aggregated metrics, no individual user data
            assert 'email' not in str(data_dict)
            assert 'phone' not in str(data_dict)
            assert 'address' not in str(data_dict)
            
            # Verify we have proper aggregated data
            assert 'total_workflows' in data_dict
            assert 'failure_rate_percent' in data_dict
    
    def test_p4_observability_metrics(self):
        """Test P-4: Proper metrics emission"""
        response = self.client.get("/metrics")
        assert response.status_code == 200
        
        metrics = response.json()
        
        # Verify required metrics are present
        assert "analytics_reports_generated_total" in metrics
        assert "analytics_service_uptime_seconds" in metrics
        
        # Verify metrics are numeric
        for key, value in metrics.items():
            assert isinstance(value, (int, float))
    
    def test_p5_multi_tenant_isolation(self):
        """Test P-5: Multi-tenant data isolation"""
        default_tenant = "00000000-0000-0000-0000-000000000001"
        
        # Get tenant-specific data
        tenant_overview = self.analytics.get_analytics_overview(default_tenant)
        assert len(tenant_overview) == 1
        assert tenant_overview[0].tenant_id == default_tenant
        
        # Verify tenant isolation in API
        response = self.client.get(f"/reports/tenant/{default_tenant}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["tenant_id"] == default_tenant
        
        # Verify no cross-tenant data leakage
        fake_tenant = "99999999-9999-9999-9999-999999999999"
        response = self.client.get(f"/reports/tenant/{fake_tenant}")
        assert response.status_code == 404
    
    def test_p6_performance_budget(self):
        """Test P-6: Response time within budget"""
        import time
        
        # Test multiple endpoints for performance
        endpoints = [
            "/healthz",
            "/reports/overview",
            "/reports/mttr",
            "/reports/costs"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.client.get(endpoint)
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            
            # Should be well under 800ms budget
            assert response_time_ms < 800, f"Endpoint {endpoint} took {response_time_ms}ms"
            assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])