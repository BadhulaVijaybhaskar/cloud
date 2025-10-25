#!/usr/bin/env python3
"""
S3 audit logger for ATOM workflow operations.
Provides immutable audit logging with SHA-256 verification.
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AuditEvent:
    """Audit event structure."""
    timestamp: str
    event_type: str
    user_id: str
    tenant_id: str
    resource_type: str
    resource_id: str
    action: str
    outcome: str
    details: Dict[str, Any]
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(',', ':'))
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the audit event."""
        event_json = self.to_json()
        return hashlib.sha256(event_json.encode('utf-8')).hexdigest()

class S3AuditLogger:
    """S3-based audit logger with integrity verification."""
    
    def __init__(self, bucket_name: Optional[str] = None, prefix: str = "audit-logs"):
        self.bucket_name = bucket_name or os.getenv("S3_AUDIT_BUCKET")
        self.prefix = prefix
        self.s3_client = None
        
        # Initialize S3 client if credentials available
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=os.getenv("S3_ENDPOINT"),
                aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
                aws_secret_access_key=os.getenv("S3_SECRET_KEY")
            )
            if self.bucket_name:
                self._ensure_bucket_exists()
        except (NoCredentialsError, ClientError) as e:
            logger.warning(f"S3 not configured, using local audit logging: {e}")
    
    def _ensure_bucket_exists(self):
        """Ensure audit bucket exists."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.info(f"Creating audit bucket: {self.bucket_name}")
                self.s3_client.create_bucket(Bucket=self.bucket_name)
    
    def log_event(self, event: AuditEvent) -> str:
        """Log audit event and return hash."""
        event_hash = event.calculate_hash()
        
        # Add hash to event details for verification
        event.details['audit_hash'] = event_hash
        
        if self.s3_client and self.bucket_name:
            self._log_to_s3(event, event_hash)
        else:
            self._log_to_file(event, event_hash)
        
        return event_hash
    
    def _log_to_s3(self, event: AuditEvent, event_hash: str):
        """Log event to S3."""
        try:
            # Create object key with timestamp and hash
            timestamp = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
            date_prefix = timestamp.strftime('%Y/%m/%d')
            object_key = f"{self.prefix}/{date_prefix}/{event_hash}.json"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=event.to_json(),
                ContentType='application/json',
                Metadata={
                    'event-type': event.event_type,
                    'tenant-id': event.tenant_id,
                    'audit-hash': event_hash
                }
            )
            
            logger.info(f"Audit event logged to S3: {object_key}")
            
        except ClientError as e:
            logger.error(f"Failed to log audit event to S3: {e}")
            # Fallback to local logging
            self._log_to_file(event, event_hash)
    
    def _log_to_file(self, event: AuditEvent, event_hash: str):
        """Log event to local file."""
        log_dir = "logs/audit"
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file with date
        timestamp = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
        log_file = f"{log_dir}/audit-{timestamp.strftime('%Y-%m-%d')}.jsonl"
        
        with open(log_file, 'a') as f:
            f.write(event.to_json() + '\\n')
        
        logger.info(f"Audit event logged to file: {log_file}")
    
    def verify_event_integrity(self, event_data: Dict[str, Any]) -> bool:
        """Verify audit event integrity using stored hash."""
        stored_hash = event_data.get('details', {}).get('audit_hash')
        if not stored_hash:
            logger.warning("No audit hash found in event data")
            return False
        
        # Remove hash from details for verification
        event_copy = event_data.copy()
        event_copy['details'] = event_copy['details'].copy()
        del event_copy['details']['audit_hash']
        
        # Recalculate hash
        event_json = json.dumps(event_copy, separators=(',', ':'))
        calculated_hash = hashlib.sha256(event_json.encode('utf-8')).hexdigest()
        
        return calculated_hash == stored_hash
    
    def verify_log_integrity(self, log_file: str) -> Dict[str, Any]:
        """Verify integrity of entire log file."""
        results = {
            "file": log_file,
            "total_events": 0,
            "verified_events": 0,
            "failed_events": 0,
            "corrupted_events": []
        }
        
        try:
            with open(log_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        results["total_events"] += 1
                        try:
                            event_data = json.loads(line.strip())
                            if self.verify_event_integrity(event_data):
                                results["verified_events"] += 1
                            else:
                                results["failed_events"] += 1
                                results["corrupted_events"].append({
                                    "line": line_num,
                                    "event_type": event_data.get("event_type", "unknown"),
                                    "timestamp": event_data.get("timestamp", "unknown")
                                })
                        except json.JSONDecodeError:
                            results["failed_events"] += 1
                            results["corrupted_events"].append({
                                "line": line_num,
                                "error": "Invalid JSON"
                            })
        
        except FileNotFoundError:
            results["error"] = "Log file not found"
        
        return results

def create_audit_event(
    event_type: str,
    user_id: str,
    tenant_id: str,
    resource_type: str,
    resource_id: str,
    action: str,
    outcome: str,
    details: Dict[str, Any],
    source_ip: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditEvent:
    """Factory function to create audit event."""
    return AuditEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_type=event_type,
        user_id=user_id,
        tenant_id=tenant_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        outcome=outcome,
        details=details,
        source_ip=source_ip,
        user_agent=user_agent
    )

def main():
    """CLI interface for audit logger."""
    import argparse
    
    parser = argparse.ArgumentParser(description="S3 Audit Logger")
    parser.add_argument("--verify", choices=["sha", "file"], help="Verify audit log integrity")
    parser.add_argument("--log-file", help="Log file to verify")
    parser.add_argument("--test", action="store_true", help="Run test audit events")
    
    args = parser.parse_args()
    
    logger = S3AuditLogger()
    
    if args.verify == "sha" and args.log_file:
        results = logger.verify_log_integrity(args.log_file)
        print(json.dumps(results, indent=2))
    
    elif args.verify == "sha":
        # Verify all audit log files
        log_dir = "logs/audit"
        if os.path.exists(log_dir):
            for filename in os.listdir(log_dir):
                if filename.endswith('.jsonl'):
                    log_file = os.path.join(log_dir, filename)
                    results = logger.verify_log_integrity(log_file)
                    print(f"Verification results for {filename}:")
                    print(json.dumps(results, indent=2))
        else:
            print("No audit logs found")
    
    elif args.test:
        # Create test audit events
        test_events = [
            create_audit_event(
                "workflow_execution",
                "user123",
                "tenant456", 
                "workflow",
                "wf-789",
                "execute",
                "success",
                {"duration_ms": 1500, "steps_completed": 5}
            ),
            create_audit_event(
                "workflow_upload",
                "user123",
                "tenant456",
                "workflow",
                "wf-790",
                "upload",
                "success",
                {"signed": True, "size_bytes": 2048}
            )
        ]
        
        for event in test_events:
            event_hash = logger.log_event(event)
            print(f"Logged event: {event.event_type} (hash: {event_hash[:16]}...)")

if __name__ == "__main__":
    main()