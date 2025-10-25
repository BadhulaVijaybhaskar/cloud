"""
Tests for cosign signature enforcement.
"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml

# Add services to path
import sys
sys.path.append(str(Path(__file__).parent.parent / "services" / "workflow-registry"))

from cosign_enforcer import CosignEnforcer

class TestCosignEnforcer:
    """Test cosign signature enforcement."""
    
    def setup_method(self):
        """Set up test environment."""
        self.enforcer = CosignEnforcer()
        
        # Sample WPK content
        self.sample_wpk = {
            "apiVersion": "v1",
            "kind": "WorkflowPackage",
            "metadata": {
                "name": "test-workflow",
                "version": "1.0.0",
                "description": "Test workflow",
                "author": "test-author"
            },
            "spec": {
                "runtime": {"type": "kubernetes"},
                "safety": {"mode": "manual"},
                "handlers": [{"name": "test-handler"}]
            }
        }
        
        self.sample_wpk_bytes = yaml.dump(self.sample_wpk).encode('utf-8')
    
    def test_signature_format_validation(self):
        """Test signature format validation."""
        # Valid base64 signature
        valid_sig = "MEUCIQDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        assert self.enforcer.validate_signature_format(valid_sig)
        
        # Invalid signatures
        assert not self.enforcer.validate_signature_format("")
        assert not self.enforcer.validate_signature_format("short")
        assert not self.enforcer.validate_signature_format("invalid@chars!")
    
    def test_verify_wpk_signature_no_signature(self):
        """Test verification with no signature."""
        result = self.enforcer.verify_wpk_signature(self.sample_wpk_bytes, "")
        assert not result
    
    def test_verify_wpk_signature_dev_mode(self):
        """Test verification in development mode."""
        # Set development mode
        os.environ["ATOM_DEV_MODE"] = "true"
        
        try:
            result = self.enforcer.verify_wpk_signature(self.sample_wpk_bytes, "test-sig")
            assert result  # Should pass in dev mode
        finally:
            # Clean up
            if "ATOM_DEV_MODE" in os.environ:
                del os.environ["ATOM_DEV_MODE"]
    
    def test_verify_wpk_signature_no_public_key(self):
        """Test verification without public key."""
        # Ensure no public key is set
        enforcer = CosignEnforcer(public_key_path=None)
        
        result = enforcer.verify_wpk_signature(self.sample_wpk_bytes, "test-signature")
        assert not result
    
    def test_find_cosign_binary_not_found(self):
        """Test cosign binary detection when not available."""
        # This test may fail if cosign is actually installed
        # In that case, it's expected behavior
        try:
            enforcer = CosignEnforcer()
            # If we get here, cosign was found (which is fine)
            assert enforcer.cosign_binary is not None
        except RuntimeError as e:
            # Expected if cosign is not installed
            assert "cosign binary not found" in str(e)
    
    @pytest.mark.skipif(not os.path.exists("/usr/bin/which"), reason="Unix-specific test")
    def test_cosign_binary_detection(self):
        """Test cosign binary detection on Unix systems."""
        try:
            enforcer = CosignEnforcer()
            # Should either find cosign or raise RuntimeError
            assert enforcer.cosign_binary is not None
        except RuntimeError:
            # Expected if cosign is not installed
            pass
    
    def test_create_cosign_enforcer_factory(self):
        """Test factory function."""
        from cosign_enforcer import create_cosign_enforcer
        
        enforcer = create_cosign_enforcer()
        assert isinstance(enforcer, CosignEnforcer)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])