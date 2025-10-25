#!/usr/bin/env python3
"""
ETL export for workflow runs to JSONL format.
Exports workflow execution data for NeuralOps training and analysis.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Iterator
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowRunsExporter:
    """Export workflow runs to JSONL format."""
    
    def __init__(self, db_dsn: Optional[str] = None):
        self.db_dsn = db_dsn or os.getenv("POSTGRES_DSN")
        self.use_sqlite = not self.db_dsn
        self.sqlite_path = "test_runs.db"  # Fallback SQLite database
    
    def export_to_jsonl(self, output_file: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Export workflow runs to JSONL file."""
        results = {
            "export_file": output_file,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "unknown",
            "records_exported": 0,
            "errors": []
        }
        
        try:
            if self.use_sqlite:
                results.update(self._export_from_sqlite(output_file, limit))
            else:
                results.update(self._export_from_postgres(output_file, limit))
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            results["status"] = "failed"
            results["errors"].append(str(e))
        
        return results
    
    def _export_from_postgres(self, output_file: str, limit: Optional[int]) -> Dict[str, Any]:
        """Export from PostgreSQL database."""
        results = {"source": "postgresql", "records_exported": 0}
        
        with psycopg2.connect(self.db_dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                
                # Build query
                query = """
                    SELECT 
                        id,
                        tenant_id,
                        workflow_name,
                        workflow_version,
                        status,
                        started_at,
                        completed_at,
                        duration_ms,
                        steps_completed,
                        steps_total,
                        error_message,
                        metadata,
                        created_at
                    FROM workflow_runs
                    ORDER BY created_at DESC
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cur.execute(query)
                
                # Export to JSONL
                with open(output_file, 'w') as f:
                    for row in cur:
                        # Convert row to dict and handle datetime serialization
                        record = dict(row)
                        record = self._serialize_record(record)
                        
                        f.write(json.dumps(record, separators=(',', ':')) + '\\n')
                        results["records_exported"] += 1
        
        results["status"] = "success"
        logger.info(f"Exported {results['records_exported']} records from PostgreSQL")
        return results
    
    def _export_from_sqlite(self, output_file: str, limit: Optional[int]) -> Dict[str, Any]:
        """Export from SQLite database (fallback)."""
        results = {"source": "sqlite", "records_exported": 0}
        
        # Create sample data if SQLite doesn't exist
        if not os.path.exists(self.sqlite_path):
            self._create_sample_data()
        
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            # Build query
            query = """
                SELECT 
                    id,
                    tenant_id,
                    workflow_name,
                    workflow_version,
                    status,
                    started_at,
                    completed_at,
                    duration_ms,
                    steps_completed,
                    steps_total,
                    error_message,
                    metadata,
                    created_at
                FROM workflow_runs
                ORDER BY created_at DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cur.execute(query)
            
            # Export to JSONL
            with open(output_file, 'w') as f:
                for row in cur:
                    # Convert row to dict
                    record = dict(row)
                    record = self._serialize_record(record)
                    
                    f.write(json.dumps(record, separators=(',', ':')) + '\\n')
                    results["records_exported"] += 1
        
        results["status"] = "success"
        logger.info(f"Exported {results['records_exported']} records from SQLite")
        return results
    
    def _serialize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize record for JSON export."""
        # Handle datetime fields
        datetime_fields = ['started_at', 'completed_at', 'created_at']
        for field in datetime_fields:
            if record.get(field):
                if isinstance(record[field], str):
                    # Already a string, keep as-is
                    pass
                else:
                    # Convert datetime to ISO string
                    record[field] = record[field].isoformat()
        
        # Handle JSON fields
        if record.get('metadata') and isinstance(record['metadata'], str):
            try:
                record['metadata'] = json.loads(record['metadata'])
            except json.JSONDecodeError:
                # Keep as string if not valid JSON
                pass
        
        # Add export metadata
        record['_export_timestamp'] = datetime.now(timezone.utc).isoformat()
        record['_export_version'] = '1.0'
        
        return record
    
    def _create_sample_data(self):
        """Create sample workflow runs data for testing."""
        logger.info(f"Creating sample data in {self.sqlite_path}")
        
        with sqlite3.connect(self.sqlite_path) as conn:
            cur = conn.cursor()
            
            # Create table
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
            
            # Insert sample data
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
                    'metadata': '{"target_latency": 200, "current_replicas": 3, "max_replicas": 10}',
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
                """, (
                    run['id'], run['tenant_id'], run['workflow_name'], 
                    run['workflow_version'], run['status'], run['started_at'],
                    run['completed_at'], run['duration_ms'], run['steps_completed'],
                    run['steps_total'], run['error_message'], run['metadata'],
                    run['created_at']
                ))
            
            conn.commit()
            logger.info(f"Created {len(sample_runs)} sample workflow runs")

def main():
    """CLI interface for ETL export."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Export workflow runs to JSONL")
    parser.add_argument("--output", default="workflow_runs_export.jsonl", 
                       help="Output JSONL file")
    parser.add_argument("--limit", type=int, help="Limit number of records")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    exporter = WorkflowRunsExporter()
    results = exporter.export_to_jsonl(args.output, args.limit)
    
    print(json.dumps(results, indent=2))
    
    if results["status"] == "success":
        print(f"\\nExport completed: {results['records_exported']} records exported to {args.output}")
    else:
        print(f"\\nExport failed: {results.get('errors', ['Unknown error'])}")

if __name__ == "__main__":
    main()