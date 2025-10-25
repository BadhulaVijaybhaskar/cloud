"""
LangGraph run logger - persists workflow runs to DB and optionally to Milvus
"""

import os
import json
import uuid
import sqlite3
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Database configuration
POSTGRES_DSN = os.getenv("POSTGRES_DSN")
MILVUS_ENDPOINT = os.getenv("MILVUS_ENDPOINT")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Global SQLite connection for testing
_sqlite_conn = None

def get_db_connection():
    """Get database connection - postgres or sqlite fallback"""
    global _sqlite_conn
    
    if POSTGRES_DSN:
        try:
            import psycopg2
            import psycopg2.extras
            conn = psycopg2.connect(POSTGRES_DSN)
            conn.autocommit = True
            return conn, "postgres"
        except Exception as e:
            logger.warning(f"Postgres connection failed: {e}, falling back to sqlite")
    
    # SQLite fallback - use persistent connection for testing
    if _sqlite_conn is None:
        _sqlite_conn = sqlite3.connect("test_runs.db", check_same_thread=False)
        _sqlite_conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id TEXT PRIMARY KEY,
                wpk_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                inputs TEXT,
                outputs TEXT,
                status TEXT NOT NULL,
                duration_ms INTEGER,
                node_logs TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        _sqlite_conn.commit()
    
    return _sqlite_conn, "sqlite"

def generate_embedding(text: str) -> Optional[list]:
    """Generate embedding using OpenAI API if key available"""
    if not OPENAI_KEY or not text:
        return None
    
    try:
        import openai
        openai.api_key = OPENAI_KEY
        
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']
    except Exception as e:
        logger.warning(f"OpenAI embedding failed: {e}")
        return None

def upsert_to_milvus(run_id: str, embedding: list, metadata: Dict[str, Any]) -> bool:
    """Upsert embedding to Milvus if endpoint available"""
    if not MILVUS_ENDPOINT or not embedding:
        return False
    
    try:
        from pymilvus import connections, Collection, utility
        
        # Connect to Milvus
        connections.connect("default", host=MILVUS_ENDPOINT.split(":")[0], port=MILVUS_ENDPOINT.split(":")[1])
        
        # Create collection if not exists
        collection_name = "workflow_runs"
        if not utility.has_collection(collection_name):
            from pymilvus import CollectionSchema, FieldSchema, DataType
            
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
                FieldSchema(name="wpk_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="status", dtype=DataType.VARCHAR, max_length=50)
            ]
            schema = CollectionSchema(fields, "Workflow run embeddings")
            Collection(collection_name, schema)
        
        collection = Collection(collection_name)
        
        # Upsert data
        data = [
            [run_id],
            [embedding],
            [metadata.get("wpk_id", "")],
            [metadata.get("status", "")]
        ]
        collection.insert(data)
        collection.flush()
        
        logger.info(f"Upserted embedding for run {run_id} to Milvus")
        return True
        
    except Exception as e:
        logger.warning(f"Milvus upsert failed: {e}")
        return False

def log_run(run_obj: Dict[str, Any]) -> str:
    """
    Log workflow run to database and optionally to Milvus
    
    Args:
        run_obj: Dictionary containing run data with keys:
            - wpk_id: Workflow package ID
            - run_id: Unique run identifier
            - inputs: Input parameters (dict)
            - outputs: Output results (dict)
            - status: Run status (completed, failed, etc.)
            - duration_ms: Execution duration in milliseconds
            - node_logs: Execution logs (list/dict)
    
    Returns:
        str: The run_id of the logged run
    """
    
    # Validate required fields
    required_fields = ["wpk_id", "run_id", "status"]
    for field in required_fields:
        if field not in run_obj:
            raise ValueError(f"Missing required field: {field}")
    
    # Generate UUID if not provided
    db_id = str(uuid.uuid4())
    run_id = run_obj["run_id"]
    
    # Get database connection
    conn, db_type = get_db_connection()
    
    try:
        if db_type == "postgres":
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO workflow_runs (id, wpk_id, run_id, inputs, outputs, status, duration_ms, node_logs)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                db_id,
                run_obj["wpk_id"],
                run_id,
                json.dumps(run_obj.get("inputs", {})),
                json.dumps(run_obj.get("outputs", {})),
                run_obj["status"],
                run_obj.get("duration_ms"),
                json.dumps(run_obj.get("node_logs", []))
            ))
        else:  # sqlite
            conn.execute("""
                INSERT INTO workflow_runs (id, wpk_id, run_id, inputs, outputs, status, duration_ms, node_logs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                db_id,
                run_obj["wpk_id"],
                run_id,
                json.dumps(run_obj.get("inputs", {})),
                json.dumps(run_obj.get("outputs", {})),
                run_obj["status"],
                run_obj.get("duration_ms"),
                json.dumps(run_obj.get("node_logs", []))
            ))
        
        logger.info(f"Logged run {run_id} to database ({db_type})")
        
        # Handle embedding and Milvus upsert if OpenAI key available
        outputs = run_obj.get("outputs", {})
        if OPENAI_KEY and outputs.get("text"):
            embedding = generate_embedding(outputs["text"])
            if embedding:
                upsert_to_milvus(run_id, embedding, {
                    "wpk_id": run_obj["wpk_id"],
                    "status": run_obj["status"]
                })
        
        return run_id
        
    except Exception as e:
        logger.error(f"Failed to log run {run_id}: {e}")
        raise
    finally:
        if db_type == "postgres":
            conn.close()

def get_runs_by_wpk_id(wpk_id: str, limit: int = 20, offset: int = 0) -> list:
    """Get runs for a specific workflow package"""
    conn, db_type = get_db_connection()
    
    try:
        if db_type == "postgres":
            cursor = conn.cursor()
            cursor.execute("""
                SELECT run_id, status, duration_ms, created_at
                FROM workflow_runs 
                WHERE wpk_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """, (wpk_id, limit, offset))
            return cursor.fetchall()
        else:  # sqlite
            cursor = conn.execute("""
                SELECT run_id, status, duration_ms, created_at
                FROM workflow_runs 
                WHERE wpk_id = ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (wpk_id, limit, offset))
            return cursor.fetchall()
            
    except Exception as e:
        logger.error(f"Failed to get runs for {wpk_id}: {e}")
        return []
    finally:
        if db_type == "postgres":
            conn.close()