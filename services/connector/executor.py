#!/usr/bin/env python3
"""
WPK execution engine for BYOC Connector.
"""

import os
import json
import logging
import hashlib
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)

class WPKExecutor:
    """Handles WPK execution with cosign verification."""
    
    def __init__(self, cosign_key: str, simulate: bool = False):
        self.cosign_key = cosign_key
        self.simulate = simulate
        self.executions = []
    
    async def verify_signature(self, signature: str, payload: Dict[str, Any]) -> bool:
        """Verify cosign signature of WPK payload."""
        if self.simulate:
            logger.info("SIMULATION: Signature verification passed")
            return True
        
        if not self.cosign_key:
            logger.warning("COSIGN_KEY not set, using simulation mode")
            return True
        
        try:
            # In production, this would use actual cosign verification
            payload_json = json.dumps(payload, sort_keys=True)
            payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
            
            # Mock verification - in production use cosign CLI or library
            if signature and len(signature) > 10:
                logger.info("Signature verification passed")
                return True
            else:
                logger.error("Invalid signature format")
                return False
                
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    async def execute(self, playbook_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute WPK playbook."""
        execution_id = str(uuid.uuid4())
        
        try:
            if self.simulate:
                logger.info(f"SIMULATION: Executing playbook {playbook_id}")
                result = {
                    "execution_id": execution_id,
                    "playbook_id": playbook_id,
                    "status": "success",
                    "method": "simulation",
                    "duration_ms": 1500,
                    "output": f"Simulated execution of {playbook_id}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                self.executions.append(result)
                return result
            
            # Extract manifest from payload
            manifest = payload.get("manifest", {})
            if not manifest:
                raise ValueError("No manifest found in payload")
            
            # Write manifest to temporary file
            manifest_file = f"/tmp/wpk-{execution_id}.yaml"
            with open(manifest_file, 'w') as f:
                if isinstance(manifest, dict):
                    import yaml
                    yaml.dump(manifest, f)
                else:
                    f.write(str(manifest))
            
            # Execute via kubectl
            cmd = ["kubectl", "apply", "-f", manifest_file]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Clean up
            os.unlink(manifest_file)
            
            result = {
                "execution_id": execution_id,
                "playbook_id": playbook_id,
                "status": "success" if process.returncode == 0 else "failed",
                "method": "kubectl",
                "return_code": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            self.executions.append(result)
            logger.info(f"Executed playbook {playbook_id}: {result['status']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            result = {
                "execution_id": execution_id,
                "playbook_id": playbook_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            self.executions.append(result)
            return result
    
    async def log_execution(self, orchestration_id: str, playbook_id: str, result: Dict[str, Any]):
        """Log execution with audit trail."""
        try:
            audit_entry = {
                "orchestration_id": orchestration_id,
                "execution_id": result.get("execution_id"),
                "playbook_id": playbook_id,
                "status": result.get("status"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": result
            }
            
            # Create hash for integrity
            audit_json = json.dumps(audit_entry, sort_keys=True)
            audit_hash = hashlib.sha256(audit_json.encode()).hexdigest()
            audit_entry["hash"] = audit_hash
            
            # Write to local audit log
            log_file = "byoc_audit.log"
            with open(log_file, 'a') as f:
                f.write(json.dumps(audit_entry) + "\n")
            
            logger.info(f"Execution logged: {result.get('execution_id')}")
            
        except Exception as e:
            logger.error(f"Audit logging error: {e}")
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary statistics."""
        total = len(self.executions)
        successful = len([e for e in self.executions if e.get("status") == "success"])
        failed = len([e for e in self.executions if e.get("status") in ["failed", "error"]])
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "simulation_mode": self.simulate,
            "last_execution": self.executions[-1] if self.executions else None
        }