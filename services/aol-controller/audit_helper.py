#!/usr/bin/env python3
"""
Audit Helper - Pre/post snapshots and cosign signing for P2/P7 compliance
Phase I.6.5 - Audit Helper implementation
"""

import os
import json
import hashlib
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

class AuditHelper:
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.vault_addr = os.getenv("VAULT_ADDR")
        self.cosign_key_path = os.getenv("COSIGN_KEY_PATH")
        
        # Audit storage (in production would use persistent storage)
        self.audit_log = []
        self.snapshots = {}
    
    def take_snapshot(self, snapshot_id: str, context: Optional[Dict] = None) -> str:
        """Take system state snapshot for P7 compliance"""
        timestamp = time.time()
        
        if self.simulation_mode:
            # Simulate snapshot creation
            snapshot_data = self._generate_simulated_snapshot(context)
        else:
            # In production: collect actual system state
            snapshot_data = self._collect_system_state(context)
        
        # Calculate SHA256 hash of snapshot
        snapshot_json = json.dumps(snapshot_data, sort_keys=True)
        snapshot_hash = hashlib.sha256(snapshot_json.encode()).hexdigest()
        
        # Store snapshot
        self.snapshots[snapshot_id] = {
            "id": snapshot_id,
            "hash": snapshot_hash,
            "timestamp": timestamp,
            "data": snapshot_data,
            "context": context or {}
        }
        
        # Log snapshot creation
        self._log_audit_event("snapshot_created", {
            "snapshot_id": snapshot_id,
            "hash": snapshot_hash,
            "timestamp": timestamp
        })
        
        return snapshot_hash
    
    def _generate_simulated_snapshot(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate simulated system state snapshot"""
        return {
            "services": {
                "aol-controller": {"status": "running", "version": "1.0.0", "replicas": 1},
                "global-router": {"status": "running", "version": "2.1.0", "replicas": 3},
                "neural-fabric": {"status": "running", "version": "1.5.0", "replicas": 2},
                "policy-engine": {"status": "running", "version": "1.2.0", "replicas": 2}
            },
            "configurations": {
                "scheduler.cpu_limit": 1.0,
                "scheduler.memory_limit": "2Gi",
                "router.timeout_ms": 5000,
                "router.max_connections": 1000,
                "neural.batch_size": 32,
                "neural.model_version": "v1.2.3"
            },
            "metrics": {
                "cpu_utilization": 0.65,
                "memory_utilization": 0.72,
                "latency_p95": 185.5,
                "throughput": 1250.0,
                "error_rate": 0.012
            },
            "infrastructure": {
                "nodes": 5,
                "pods": 23,
                "persistent_volumes": 8,
                "network_policies": 12
            },
            "context": context or {},
            "simulation_mode": True
        }
    
    def _collect_system_state(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Collect actual system state (production implementation)"""
        # In production: query Kubernetes API, Prometheus, etc.
        return {
            "note": "Production state collection not implemented",
            "simulation_fallback": True
        }
    
    def record_change(self, proposal: Dict[str, Any], approver: Optional[str] = None) -> str:
        """Record optimization change in audit log with P2 signing"""
        audit_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # Create audit record
        audit_record = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "event_type": "optimization_applied",
            "proposal_id": proposal.get("id"),
            "scope": proposal.get("scope"),
            "changes": proposal.get("changes", []),
            "risk_level": proposal.get("risk_level"),
            "approver": approver,
            "pre_state_hash": proposal.get("pre_state_hash"),
            "post_state_hash": proposal.get("post_state_hash"),
            "created_by": proposal.get("created_by", "aol-system")
        }
        
        # P2 Compliance: Sign the audit record
        signature = self._sign_audit_record(audit_record)
        audit_record["signature"] = signature
        
        # Store in audit log (P7 - immutable)
        self.audit_log.append(audit_record)
        
        # Log the audit event
        self._log_audit_event("change_recorded", {
            "audit_id": audit_id,
            "proposal_id": proposal.get("id"),
            "signature": signature["signature_id"] if signature else None
        })
        
        return audit_id
    
    def _sign_audit_record(self, audit_record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sign audit record using cosign for P2 compliance"""
        if self.simulation_mode:
            # Simulate signing process
            record_json = json.dumps(audit_record, sort_keys=True)
            record_hash = hashlib.sha256(record_json.encode()).hexdigest()
            
            return {
                "signature_id": f"sim_sig_{int(time.time())}",
                "algorithm": "ECDSA-SHA256",
                "key_id": "simulation_key",
                "signature": f"sim_signature_{record_hash[:16]}",
                "timestamp": time.time(),
                "cosign_bundle": f"sim_bundle_{record_hash[:8]}",
                "simulation_mode": True
            }
        
        else:
            # In production: use actual cosign signing
            if not self.cosign_key_path or not os.path.exists(self.cosign_key_path):
                return None
            
            # Would implement actual cosign signing here
            return {
                "error": "Production cosign signing not implemented",
                "fallback": "simulation"
            }
    
    def verify_signature(self, audit_id: str) -> Dict[str, Any]:
        """Verify signature of audit record"""
        audit_record = self._get_audit_record(audit_id)
        if not audit_record:
            return {"status": "error", "message": "Audit record not found"}
        
        signature = audit_record.get("signature")
        if not signature:
            return {"status": "error", "message": "No signature found"}
        
        if self.simulation_mode:
            return {
                "status": "verified",
                "signature_id": signature.get("signature_id"),
                "algorithm": signature.get("algorithm"),
                "verified_at": time.time(),
                "simulation_mode": True
            }
        
        # In production: verify actual cosign signature
        return {"status": "not_implemented"}
    
    def _get_audit_record(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """Get audit record by ID"""
        for record in self.audit_log:
            if record.get("audit_id") == audit_id:
                return record
        return None
    
    def _log_audit_event(self, event_type: str, details: Dict[str, Any]):
        """Log audit event for observability"""
        log_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "details": details,
            "service": "aol-audit-helper"
        }
        
        # In production: send to centralized logging
        if not self.simulation_mode:
            # Would send to audit log service
            pass
    
    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve snapshot by ID"""
        return self.snapshots.get(snapshot_id)
    
    def compare_snapshots(self, before_id: str, after_id: str) -> Dict[str, Any]:
        """Compare two snapshots to show changes"""
        before_snapshot = self.snapshots.get(before_id)
        after_snapshot = self.snapshots.get(after_id)
        
        if not before_snapshot or not after_snapshot:
            return {"error": "One or both snapshots not found"}
        
        # Compare configurations
        before_config = before_snapshot["data"].get("configurations", {})
        after_config = after_snapshot["data"].get("configurations", {})
        
        changes = {}
        for key in set(before_config.keys()) | set(after_config.keys()):
            before_val = before_config.get(key)
            after_val = after_config.get(key)
            
            if before_val != after_val:
                changes[key] = {
                    "before": before_val,
                    "after": after_val,
                    "change_type": "modified" if before_val and after_val else ("added" if after_val else "removed")
                }
        
        # Compare metrics
        before_metrics = before_snapshot["data"].get("metrics", {})
        after_metrics = after_snapshot["data"].get("metrics", {})
        
        metric_changes = {}
        for metric in set(before_metrics.keys()) | set(after_metrics.keys()):
            before_val = before_metrics.get(metric)
            after_val = after_metrics.get(metric)
            
            if before_val != after_val and isinstance(before_val, (int, float)) and isinstance(after_val, (int, float)):
                change_pct = ((after_val - before_val) / before_val) * 100 if before_val != 0 else 0
                metric_changes[metric] = {
                    "before": before_val,
                    "after": after_val,
                    "change_percent": change_pct
                }
        
        return {
            "before_snapshot": before_id,
            "after_snapshot": after_id,
            "before_hash": before_snapshot["hash"],
            "after_hash": after_snapshot["hash"],
            "configuration_changes": changes,
            "metric_changes": metric_changes,
            "comparison_timestamp": time.time()
        }
    
    def get_audit_trail(self, proposal_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get audit trail for proposal or all changes"""
        if proposal_id:
            # Filter by proposal ID
            filtered_log = [
                record for record in self.audit_log
                if record.get("proposal_id") == proposal_id
            ]
        else:
            # Return all audit records
            filtered_log = self.audit_log
        
        # Sort by timestamp (newest first) and limit
        sorted_log = sorted(filtered_log, key=lambda x: x.get("timestamp", 0), reverse=True)
        return sorted_log[:limit]
    
    def validate_audit_integrity(self) -> Dict[str, Any]:
        """Validate integrity of audit log (P7 compliance)"""
        validation_results = {
            "total_records": len(self.audit_log),
            "signed_records": 0,
            "verified_signatures": 0,
            "integrity_violations": [],
            "validation_timestamp": time.time()
        }
        
        for record in self.audit_log:
            if record.get("signature"):
                validation_results["signed_records"] += 1
                
                # Verify signature
                verification = self.verify_signature(record["audit_id"])
                if verification.get("status") == "verified":
                    validation_results["verified_signatures"] += 1
                else:
                    validation_results["integrity_violations"].append({
                        "audit_id": record["audit_id"],
                        "issue": "signature_verification_failed"
                    })
        
        validation_results["integrity_score"] = (
            validation_results["verified_signatures"] / validation_results["total_records"]
            if validation_results["total_records"] > 0 else 1.0
        )
        
        return validation_results
    
    def export_audit_bundle(self, start_time: Optional[float] = None, end_time: Optional[float] = None) -> Dict[str, Any]:
        """Export audit bundle for compliance reporting"""
        if start_time is None:
            start_time = 0
        if end_time is None:
            end_time = time.time()
        
        # Filter records by time range
        filtered_records = [
            record for record in self.audit_log
            if start_time <= record.get("timestamp", 0) <= end_time
        ]
        
        # Include related snapshots
        snapshot_ids = set()
        for record in filtered_records:
            if record.get("pre_state_hash"):
                snapshot_ids.add(record.get("pre_state_hash"))
            if record.get("post_state_hash"):
                snapshot_ids.add(record.get("post_state_hash"))
        
        related_snapshots = {
            sid: snapshot for sid, snapshot in self.snapshots.items()
            if snapshot["hash"] in snapshot_ids
        }
        
        bundle = {
            "export_id": str(uuid.uuid4()),
            "export_timestamp": time.time(),
            "time_range": {"start": start_time, "end": end_time},
            "audit_records": filtered_records,
            "snapshots": related_snapshots,
            "integrity_validation": self.validate_audit_integrity(),
            "metadata": {
                "total_records": len(filtered_records),
                "total_snapshots": len(related_snapshots),
                "simulation_mode": self.simulation_mode
            }
        }
        
        return bundle