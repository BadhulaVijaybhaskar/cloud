import pytest
import requests
import json
import time
from datetime import datetime

# Service endpoints
VAULT_MANAGER_URL = "http://localhost:8101"
TRUST_PROXY_URL = "http://localhost:8102"
THREAT_SENSOR_URL = "http://localhost:8103"
AUDIT_PIPELINE_URL = "http://localhost:8104"
COMPLIANCE_MONITOR_URL = "http://localhost:8105"

class TestSecurityFabric:
    
    def test_vault_manager_health(self):
        """Test Vault Manager health endpoint"""
        response = requests.get(f"{VAULT_MANAGER_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "vault-manager"
        assert "keys_managed" in data
    
    def test_secret_rotation(self):
        """Test secret rotation functionality"""
        # Get initial status
        status_response = requests.get(f"{VAULT_MANAGER_URL}/status")
        assert status_response.status_code == 200
        initial_status = status_response.json()
        
        # Perform rotation
        rotate_response = requests.post(f"{VAULT_MANAGER_URL}/rotate")
        assert rotate_response.status_code == 200
        rotation_data = rotate_response.json()
        
        assert rotation_data["status"] == "completed"
        assert "keys_rotated" in rotation_data
        assert len(rotation_data["keys_rotated"]) > 0
        
        # Verify status changed
        new_status_response = requests.get(f"{VAULT_MANAGER_URL}/status")
        assert new_status_response.status_code == 200
        new_status = new_status_response.json()
        
        # Check that rotation timestamps are recent
        for key_name in rotation_data["keys_rotated"]:
            assert key_name in new_status["keys"]
            assert new_status["keys"][key_name]["age_days"] == 0
    
    def test_trust_proxy_health(self):
        """Test Trust Proxy health endpoint"""
        response = requests.get(f"{TRUST_PROXY_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "trust-proxy"
    
    def test_jwt_validation(self):
        """Test JWT validation functionality"""
        # Test without token (should fail)
        response = requests.get(f"{TRUST_PROXY_URL}/verify")
        assert response.status_code == 403
        
        # Test with invalid token (should fail)
        headers = {"Authorization": "Bearer invalid-token"}
        response = requests.get(f"{TRUST_PROXY_URL}/verify", headers=headers)
        assert response.status_code == 403
        
        # Test token validation endpoint
        response = requests.post(f"{TRUST_PROXY_URL}/validate-token", headers=headers)
        assert response.status_code == 401
    
    def test_threat_sensor_health(self):
        """Test Threat Sensor health endpoint"""
        response = requests.get(f"{THREAT_SENSOR_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "threat-sensor"
        assert "model_status" in data
    
    def test_anomaly_detection(self):
        """Test anomaly detection functionality"""
        # Test normal event
        normal_event = {
            "event": "user_login",
            "source_ip": "192.168.1.10",
            "payload": {"username": "testuser"}
        }
        
        response = requests.post(f"{THREAT_SENSOR_URL}/detect", json=normal_event)
        assert response.status_code == 200
        data = response.json()
        
        assert "anomaly_score" in data
        assert "is_anomaly" in data
        assert "confidence" in data
        assert "model_latency_ms" in data
        assert isinstance(data["anomaly_score"], float)
        assert 0 <= data["anomaly_score"] <= 1
        
        # Test suspicious event
        suspicious_event = {
            "event": "failed_login",
            "source_ip": "192.168.1.100",
            "payload": {"username": "admin", "query": "SELECT * FROM users UNION SELECT * FROM passwords"}
        }
        
        response = requests.post(f"{THREAT_SENSOR_URL}/detect", json=suspicious_event)
        assert response.status_code == 200
        data = response.json()
        
        # Should have higher anomaly score
        assert data["anomaly_score"] > 0.3
        assert len(data["detected_patterns"]) > 0
    
    def test_audit_pipeline_health(self):
        """Test Audit Pipeline health endpoint"""
        response = requests.get(f"{AUDIT_PIPELINE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "audit-pipeline"
    
    def test_audit_append_export(self):
        """Test audit event append and export functionality"""
        # Append audit event
        audit_event = {
            "action": "test_action",
            "actor": "test_user",
            "tenant": "test_tenant",
            "resource": "test_resource",
            "metadata": {"test": "data"}
        }
        
        append_response = requests.post(f"{AUDIT_PIPELINE_URL}/append", json=audit_event)
        assert append_response.status_code == 200
        append_data = append_response.json()
        
        assert append_data["status"] == "appended"
        assert "sequence_id" in append_data
        assert "entry_hash" in append_data
        
        # Export and verify
        export_response = requests.get(f"{AUDIT_PIPELINE_URL}/export?limit=10")
        assert export_response.status_code == 200
        export_data = export_response.json()
        
        assert "entries" in export_data
        assert export_data["count"] > 0
        
        # Find our test event
        test_entry = None
        for entry in export_data["entries"]:
            if entry.get("action") == "test_action":
                test_entry = entry
                break
        
        assert test_entry is not None
        assert test_entry["actor"] == "test_user"
        assert test_entry["tenant"] == "test_tenant"
        assert "sha256" in test_entry
    
    def test_ledger_integrity(self):
        """Test audit ledger integrity verification"""
        response = requests.get(f"{AUDIT_PIPELINE_URL}/verify")
        assert response.status_code == 200
        data = response.json()
        
        assert "valid" in data
        assert "entries_verified" in data
        assert "corrupted_entries" in data
        
        # Should have no corruption in simulation mode
        assert len(data["corrupted_entries"]) == 0
    
    def test_compliance_monitor_health(self):
        """Test Compliance Monitor health endpoint"""
        response = requests.get(f"{COMPLIANCE_MONITOR_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "compliance-monitor"
        assert data["policies_monitored"] == 6  # P1-P6
    
    def test_compliance_scan(self):
        """Test compliance scanning functionality"""
        # Run compliance scan
        scan_response = requests.get(f"{COMPLIANCE_MONITOR_URL}/scan")
        assert scan_response.status_code == 200
        scan_data = scan_response.json()
        
        assert "scan_id" in scan_data
        assert "policies" in scan_data
        assert "summary" in scan_data
        
        # Verify all P-policies are included
        expected_policies = ["P1", "P2", "P3", "P4", "P5", "P6"]
        for policy_id in expected_policies:
            assert policy_id in scan_data["policies"]
            policy_data = scan_data["policies"][policy_id]
            assert "score" in policy_data
            assert "checks" in policy_data
            assert len(policy_data["checks"]) > 0
        
        # Verify summary
        summary = scan_data["summary"]
        assert summary["total_policies"] == 6
        assert summary["total_checks"] > 0
        assert summary["overall_score"] >= 0
        
        # Should achieve at least 95% compliance in simulation
        assert summary["overall_score"] >= 95
    
    def test_compliance_report_generation(self):
        """Test compliance report generation"""
        # First run a scan
        scan_response = requests.get(f"{COMPLIANCE_MONITOR_URL}/scan")
        assert scan_response.status_code == 200
        
        # Generate report
        report_response = requests.get(f"{COMPLIANCE_MONITOR_URL}/report")
        assert report_response.status_code == 200
        report_data = report_response.json()
        
        assert "report" in report_data
        assert "report_file" in report_data
        assert "scan_id" in report_data
        
        # Verify report content
        report_content = report_data["report"]
        assert "# ATOM Cloud Compliance Report" in report_content
        assert "## Policy Compliance Matrix" in report_content
        assert "P1 Data Privacy:" in report_content
        assert "P6 Performance Budget:" in report_content
    
    def test_metrics_endpoints(self):
        """Test that all services expose Prometheus metrics"""
        services = [
            (VAULT_MANAGER_URL, "vault_keys_total"),
            (TRUST_PROXY_URL, "trust_proxy_verifications_total"),
            (THREAT_SENSOR_URL, "threat_sensor_detections_total"),
            (AUDIT_PIPELINE_URL, "audit_pipeline_events_total"),
            (COMPLIANCE_MONITOR_URL, "compliance_monitor_scans_total")
        ]
        
        for service_url, expected_metric in services:
            response = requests.get(f"{service_url}/metrics")
            assert response.status_code == 200
            metrics_text = response.text
            assert expected_metric in metrics_text
            assert "# HELP" in metrics_text
            assert "# TYPE" in metrics_text

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])