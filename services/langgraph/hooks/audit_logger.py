"""
Audit logger for immutable workflow execution records.
Generates audit records and uploads to object storage.
"""

import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AuditLogger:
    """Immutable audit logging for workflow executions."""
    
    def __init__(self, s3_client=None, bucket_name: str = "atom-audit"):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
    
    def log_workflow_event(
        self,
        workflow_run_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        user_id: str = "system"
    ) -> Optional[str]:
        """
        Log workflow event to immutable audit store.
        
        Returns:
            S3 path to audit record or None if failed
        """
        try:
            # Create audit record
            audit_record = {
                "workflow_run_id": workflow_run_id,
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "version": "1.0"
            }
            
            # Generate immutable hash
            record_json = json.dumps(audit_record, sort_keys=True)
            record_hash = hashlib.sha256(record_json.encode()).hexdigest()
            audit_record["immutable_hash"] = record_hash
            
            # Upload to S3 if available
            if self.s3_client:
                s3_path = f"audit/{datetime.utcnow().strftime('%Y/%m/%d')}/{workflow_run_id}_{event_type}_{record_hash[:8]}.json"
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_path,
                    Body=json.dumps(audit_record, indent=2),
                    ContentType="application/json"
                )
                
                logger.info(f"Audit record uploaded: {s3_path}")
                return s3_path
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return None

def create_audit_logger() -> AuditLogger:
    """Factory function for audit logger."""
    return AuditLogger()