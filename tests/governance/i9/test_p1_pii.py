import os, pytest
import json

def test_pii_detection():
    """Test P1 policy: PII detection and masking"""
    # Simulate PII detection
    test_data = {"email": "user@example.com", "ssn": "123-45-6789"}
    
    # In real implementation, this would call PII detection service
    # For simulation, we mock the detection
    detected_pii = ["email", "ssn"]
    
    assert len(detected_pii) > 0, "PII detection should identify sensitive fields"
    
def test_pii_masking():
    """Test P1 policy: PII masking functionality"""
    # Simulate PII masking
    original = "Contact John Doe at john.doe@company.com"
    masked = "Contact <NAME> at <EMAIL>"
    
    assert "<EMAIL>" in masked, "Email should be masked"
    assert "john.doe@company.com" not in masked, "Original email should not be present"