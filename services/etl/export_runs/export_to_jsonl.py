#!/usr/bin/env python3
"""
ETL export for workflow runs to JSONL format.
Exports workflow execution data for NeuralOps training and analysis.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import sqlite3
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowRunsExporter:
    """Export workflow runs to JSONL format."""
    
    def __init__(self, db_path: str = "test_runs.db"):
        self.db_path = db_path
        self.postgres_dsn = os.getenv("POSTGRES_DSN")
        
    def export_to_jsonl(self, output_file: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Export workflow runs to JSONL file."""
        results = {
            "export_file": output_file,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "unknown",
            "records_exported": 0,
            "source": "sqlite",
            "errors": []
        }
        
        try:
            # Create sample data if database doesn't exist
            if not os.path.exists(self.db_path):
                self._create_sample_data()
            
            # Export from SQLite
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                
                query = """
                    SELECT 
                        id, tenant_id, workflow_name, workflow_version,
                        status, started_at, completed_at, duration_ms,
                        steps_completed, steps_total, error_message,
                        metadata, created_at
                    FROM workflow_runs
                    ORDER BY created_at DESC
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cur.execute(query)
                
                with open(output_file, 'w') as f:
                    for row in cur:
                        record = dict(row)
                        record = self._serialize_record(record)
                        f.write(json.dumps(record, separators=(',', ':')) + '\n')
                        results["records_exported"] += 1
            
            results["status"] = "success"
            logger.info(f"Exported {results['records_exported']} records to {output_file}")
            
        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(str(e))
            logger.error(f"Export failed: {e}")
        
        return results
    
    def _create_sample_data(self):
        """Create sample workflow runs data."""
        logger.info(f"Creating sample data in {self.db_path}")
        
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT,
                    workflow_name TEXT,
                    workflow_version TEXT,
                    status TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    duration_ms INTEGER,
                    steps_completed INTEGER,
                    steps_total INTEGER,
                    error_message TEXT,
                    metadata TEXT,
                    created_at TEXT
                )
            """)
            
            sample_runs = [
                {
                    'id': 'run-001',
                    'tenant_id': '11111111-1111-1111-1111-111111111111',
                    'workflow_name': 'backup-verify',
                    'workflow_version': '1.0.0',
                    'status': 'completed',
                    'started_at': '2024-10-25T10:00:00Z',
                    'completed_at': '2024-10-25T10:02:30Z',
                    'duration_ms': 150000,
                    'steps_completed': 3,
                    'steps_total': 3,
                    'error_message': None,
                    'metadata': '{"backup_size": 1024000, "verification_passed": true}',
                    'created_at': '2024-10-25T10:00:00Z'
                },
                {
                    'id': 'run-002',
                    'tenant_id': '22222222-2222-2222-2222-222222222222',
                    'workflow_name': 'restart-unhealthy',
                    'workflow_version': '1.1.0',
                    'status': 'failed',
                    'started_at': '2024-10-25T11:00:00Z',
                    'completed_at': '2024-10-25T11:01:15Z',
                    'duration_ms': 75000,
                    'steps_completed': 2,
                    'steps_total': 4,
                    'error_message': 'Pod not found: unhealthy-service',
                    'metadata': '{"target_pods": ["unhealthy-service"], "namespace": "production"}',
                    'created_at': '2024-10-25T11:00:00Z'
                },
                {
                    'id': 'run-003',
                    'tenant_id': '11111111-1111-1111-1111-111111111111',
                    'workflow_name': 'scale-on-latency',
                    'workflow_version': '2.0.0',
                    'status': 'running',
                    'started_at': '2024-10-25T12:00:00Z',
                    'completed_at': None,
                    'duration_ms': None,
                    'steps_completed': 1,
                    'steps_total': 3,
                    'error_message': None,
                    'metadata': '{"target_latency": 200, "current_replicas": 3}',
                    'created_at': '2024-10-25T12:00:00Z'
                }
            ]
            
            for run in sample_runs:
                cur.execute("""
                    INSERT OR REPLACE INTO workflow_runs 
                    (id, tenant_id, workflow_name, workflow_version, status, 
                     started_at, completed_at, duration_ms, steps_completed, 
                     steps_total, error_message, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(run.values()))
            
            conn.commit()
    
    def _serialize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize record for JSON export."""
        # Handle JSON metadata field
        if record.get('metadata') and isinstance(record['metadata'], str):
            try:
                record['metadata'] = json.loads(record['metadata'])
            except json.JSONDecodeError:
                pass
        
        # Add export metadata
        record['_export_timestamp'] = datetime.now(timezone.utc).isoformat()
        record['_export_version'] = '1.0'
        
        return record

def main():
    """CLI interface for ETL export."""
    parser = argparse.ArgumentParser(description="Export workflow runs to JSONL")
    parser.add_argument("--output", default="workflow_runs_export.jsonl", help="Output JSONL file")
    parser.add_argument("--limit", type=int, help="Limit number of records")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    exporter = WorkflowRunsExporter()
    results = exporter.export_to_jsonl(args.output, args.limit)
    
    print(json.dumps(results, indent=2))
    
    if results["status"] == "success":
        print(f"\nExport completed: {results['records_exported']} records exported to {args.output}")
    else:
        print(f"\nExport failed: {results.get('errors', ['Unknown error'])}")

if __name__ == "__main__":
    main()