"""
Tests for Vault integration functionality.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "workflow-registry"))
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "runtime-agent"))

class TestVaultClient:
    """Test Vault client functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear environment variables
        for key in ["VAULT_ADDR", "VAULT_TOKEN", "VAULT_ROLE_ID", "VAULT_SECRET_ID"]:
            if key in os.environ:
                del os.environ[key]
    
    def test_vault_client_creation_no_addr(self):
        """Test Vault client creation without VAULT_ADDR."""
        import secrets as vault_secrets
        VaultClient = vault_secrets.VaultClient
        
        with pytest.raises(ValueError, match="VAULT_ADDR"):
            VaultClient()
    
    def test_vault_client_creation_with_token(self):
        """Test Vault client creation with token."""
        import secrets as vault_secrets
        VaultClient = vault_secrets.VaultClient
        
        os.environ["VAULT_ADDR"] = "https://vault.example.com:8200"
        os.environ["VAULT_TOKEN"] = "test-token"
        
        client = VaultClient()
        assert client.vault_addr == "https://vault.example.com:8200"
        assert client.token == "test-token"
    
    @patch('requests.Session.post')
    def test_approle_authentication(self, mock_post):
        """Test AppRole authentication."""
        import secrets as vault_secrets
        VaultClient = vault_secrets.VaultClient
        
        # Mock successful AppRole response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "auth": {"client_token": "approle-token"}
        }
        mock_post.return_value = mock_response
        
        os.environ["VAULT_ADDR"] = "https://vault.example.com:8200"
        os.environ["VAULT_ROLE_ID"] = "test-role-id"
        os.environ["VAULT_SECRET_ID"] = "test-secret-id"
        
        client = VaultClient()
        assert client.token == "approle-token"
        
        # Verify AppRole login was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "auth/approle/login" in call_args[0][0]
    
    @patch('requests.Session.get')
    def test_get_secret_success(self, mock_get):
        """Test successful secret retrieval."""
        import secrets as vault_secrets
        VaultClient = vault_secrets.VaultClient
        
        # Mock successful secret response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": {
                "data": {
                    "public_key": "test-cosign-key",
                    "private_key": "test-private-key"
                }
            }
        }
        mock_get.return_value = mock_response
        
        os.environ["VAULT_ADDR"] = "https://vault.example.com:8200"
        os.environ["VAULT_TOKEN"] = "test-token"
        
        client = VaultClient()
        
        # Test getting specific key
        public_key = client.get_secret("atom/cosign", "public_key")
        assert public_key == "test-cosign-key"
        
        # Test getting entire secret
        full_secret = client.get_secret("atom/cosign")
        assert full_secret["public_key"] == "test-cosign-key"
        assert full_secret["private_key"] == "test-private-key"
    
    @patch('requests.Session.get')
    def test_health_check(self, mock_get):
        """Test Vault health check."""
        import secrets as vault_secrets
        VaultClient = vault_secrets.VaultClient
        
        # Mock health responses
        health_response = Mock()
        health_response.status_code = 200
        
        token_response = Mock()
        token_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [health_response, token_response]
        
        os.environ["VAULT_ADDR"] = "https://vault.example.com:8200"
        os.environ["VAULT_TOKEN"] = "test-token"
        
        client = VaultClient()
        assert client.health_check() is True
    
    def test_create_vault_client_factory_no_addr(self):
        """Test factory function without VAULT_ADDR."""
        import secrets as vault_secrets
        create_vault_client = vault_secrets.create_vault_client
        
        client = create_vault_client()
        assert client is None
    
    def test_create_vault_client_factory_success(self):
        """Test successful factory function."""
        import secrets as vault_secrets
        
        with patch.object(vault_secrets, 'VaultClient') as mock_vault_client:
        
        # Mock successful client creation
        mock_client = Mock()
        mock_client.health_check.return_value = True
        mock_vault_client.return_value = mock_client
        
        os.environ["VAULT_ADDR"] = "https://vault.example.com:8200"
        
            # Mock successful client creation
            mock_client = Mock()
            mock_client.health_check.return_value = True
            mock_vault_client.return_value = mock_client
            
            os.environ["VAULT_ADDR"] = "https://vault.example.com:8200"
            
            client = vault_secrets.create_vault_client()
            assert client is not None

class TestSecretHelpers:
    """Test secret helper functions."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear environment variables
        for key in ["VAULT_ADDR", "COSIGN_PUBLIC_KEY_PATH", "POSTGRES_DSN"]:
            if key in os.environ:
                del os.environ[key]
    
    def test_get_cosign_public_key_vault(self):
        """Test getting cosign key from Vault."""
        import secrets as vault_secrets
        
        with patch.object(vault_secrets, 'create_vault_client') as mock_create_client:
        
        # Mock Vault client
        mock_client = Mock()
        mock_client.get_secret.return_value = "vault-cosign-key"
        mock_create_client.return_value = mock_client
        
            key = vault_secrets.get_cosign_public_key()
            assert key == "vault-cosign-key"
            mock_client.get_secret.assert_called_once_with("atom/cosign", "public_key")
    
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_get_cosign_public_key_fallback(self, mock_exists, mock_open):
        """Test getting cosign key from file fallback."""
        import secrets as vault_secrets
        
        with patch.object(vault_secrets, 'create_vault_client') as mock_create_client:
        
        # Mock Vault unavailable
        mock_create_client.return_value = None
        
        # Mock file exists and content
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = "file-cosign-key\n"
        mock_open.return_value.__enter__.return_value = mock_file
        
        os.environ["COSIGN_PUBLIC_KEY_PATH"] = "/path/to/cosign.pub"
        
            key = vault_secrets.get_cosign_public_key()
            assert key == "file-cosign-key"
    
    def test_get_database_dsn_vault(self):
        """Test getting database DSN from Vault."""
        import secrets as vault_secrets
        
        with patch.object(vault_secrets, 'create_vault_client') as mock_create_client:
        
        # Mock Vault client
        mock_client = Mock()
        mock_client.get_secret.return_value = "postgresql://vault:password@localhost/db"
        mock_create_client.return_value = mock_client
        
            dsn = vault_secrets.get_database_dsn()
            assert dsn == "postgresql://vault:password@localhost/db"
    
    def test_get_database_dsn_fallback(self):
        """Test getting database DSN from environment fallback."""
        import secrets as vault_secrets
        
        with patch.object(vault_secrets, 'create_vault_client') as mock_create_client:
        
        # Mock Vault unavailable
        mock_create_client.return_value = None
        
        os.environ["POSTGRES_DSN"] = "postgresql://env:password@localhost/db"
        
            dsn = vault_secrets.get_database_dsn()
            assert dsn == "postgresql://env:password@localhost/db"

class TestRuntimeAgentSecrets:
    """Test runtime agent secret functions."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear environment variables
        for key in ["KUBECONFIG", "PROMETHEUS_URL"]:
            if key in os.environ:
                del os.environ[key]
    
    def test_get_kubernetes_config_vault(self):
        """Test getting kubeconfig from Vault."""
        try:
            # Import runtime agent secrets
            import sys
            runtime_path = str(Path(__file__).parent.parent / "services" / "runtime-agent")
            if runtime_path not in sys.path:
                sys.path.insert(0, runtime_path)
            
            import secrets as runtime_secrets
            
            with patch.object(runtime_secrets, 'create_vault_client') as mock_create_client:
            
            # Mock Vault client
            mock_client = Mock()
            mock_client.get_secret.return_value = "vault-kubeconfig-content"
            mock_create_client.return_value = mock_client
            
                config = runtime_secrets.get_kubernetes_config()
                assert config == "vault-kubeconfig-content"
        except ImportError:
            pytest.skip("Runtime agent secrets module not available")
    
    def test_get_api_credentials(self):
        """Test getting API credentials."""
        try:
            import sys
            runtime_path = str(Path(__file__).parent.parent / "services" / "runtime-agent")
            if runtime_path not in sys.path:
                sys.path.insert(0, runtime_path)
            
            import secrets as runtime_secrets
            
            with patch.object(runtime_secrets, 'create_vault_client') as mock_create_client:
            
            # Mock Vault client
            mock_client = Mock()
            mock_client.get_secret.return_value = {
                "url": "https://prometheus.example.com",
                "username": "admin",
                "password": "secret"
            }
            mock_create_client.return_value = mock_client
            
                creds = runtime_secrets.get_api_credentials("prometheus")
                assert creds["url"] == "https://prometheus.example.com"
                assert creds["username"] == "admin"
        except ImportError:
            pytest.skip("Runtime agent secrets module not available")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])