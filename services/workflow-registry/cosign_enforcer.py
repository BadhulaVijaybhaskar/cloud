"""
Cosign signature enforcement for WPK packages.
Provides secure signature verification using cosign public keys.
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

logger = logging.getLogger(__name__)

class CosignEnforcer:
    """Enforces cosign signature verification for WPK packages."""
    
    def __init__(self, public_key_path: Optional[str] = None):
        """Initialize with optional public key path."""
        self.public_key_path = public_key_path or os.getenv("COSIGN_PUBLIC_KEY_PATH")
        self.cosign_binary = self._find_cosign_binary()
        
    def _find_cosign_binary(self) -> str:
        """Find cosign binary in PATH."""
        try:
            result = subprocess.run(["which", "cosign"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            pass
        
        # Fallback paths
        for path in ["/usr/local/bin/cosign", "/usr/bin/cosign", "cosign"]:
            if os.path.exists(path) or path == "cosign":
                return path
        
        raise RuntimeError("cosign binary not found in PATH")
    
    def verify_wpk_signature(self, wpk_content: bytes, signature: str) -> bool:
        """
        Verify WPK signature using cosign.
        
        Args:
            wpk_content: Raw WPK file content
            signature: Base64 encoded signature
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not signature:
            logger.warning("No signature provided for WPK verification")
            return False
            
        if not self.public_key_path or not os.path.exists(self.public_key_path):
            logger.warning("No valid cosign public key configured")
            # In development mode, allow unsigned packages with warning
            if os.getenv("ATOM_DEV_MODE") == "true":
                logger.warning("Development mode: allowing unsigned WPK")
                return True
            return False
        
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.wpk.yaml', delete=False) as wpk_file:
                wpk_file.write(wpk_content)
                wpk_file_path = wpk_file.name
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sig', delete=False) as sig_file:
                sig_file.write(signature)
                sig_file_path = sig_file.name
            
            # Run cosign verify-blob
            cmd = [
                self.cosign_binary,
                "verify-blob",
                "--key", self.public_key_path,
                "--signature", sig_file_path,
                wpk_file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Cleanup temp files
            os.unlink(wpk_file_path)
            os.unlink(sig_file_path)
            
            if result.returncode == 0:
                logger.info("WPK signature verification successful")
                return True
            else:
                logger.error(f"WPK signature verification failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Cosign verification timed out")
            return False
        except Exception as e:
            logger.error(f"Error during signature verification: {e}")
            return False
    
    def sign_wpk(self, wpk_file_path: str, private_key_path: str) -> Optional[str]:
        """
        Sign WPK file using cosign (for testing/development).
        
        Args:
            wpk_file_path: Path to WPK file
            private_key_path: Path to cosign private key
            
        Returns:
            Base64 encoded signature or None if failed
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sig', delete=False) as sig_file:
                sig_file_path = sig_file.name
            
            cmd = [
                self.cosign_binary,
                "sign-blob",
                "--key", private_key_path,
                "--output-signature", sig_file_path,
                wpk_file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                with open(sig_file_path, 'r') as f:
                    signature = f.read().strip()
                os.unlink(sig_file_path)
                return signature
            else:
                logger.error(f"WPK signing failed: {result.stderr}")
                os.unlink(sig_file_path)
                return None
                
        except Exception as e:
            logger.error(f"Error during WPK signing: {e}")
            return None
    
    def validate_signature_format(self, signature: str) -> bool:
        """Validate signature format (basic checks)."""
        if not signature or len(signature) < 10:
            return False
        
        # Basic base64 pattern check
        import re
        base64_pattern = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
        return bool(base64_pattern.match(signature.replace('\n', '')))

def create_cosign_enforcer() -> CosignEnforcer:
    """Factory function to create cosign enforcer."""
    return CosignEnforcer()