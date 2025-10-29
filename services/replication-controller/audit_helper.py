# services/replication-controller/audit_helper.py
import json, hashlib, psycopg2, os
from datetime import datetime

def sha256_json(payload):
    s = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(s).hexdigest()

def write_audit(conn, job_id, action, actor, payload):
    payload_sha = sha256_json(payload)
    q = """
    INSERT INTO replication_audit (job_id, action, actor, payload, payload_sha256, created_at)
    VALUES (%s,%s,%s,%s,%s,%s)
    """
    with conn.cursor() as cur:
        cur.execute(q, (job_id, action, actor, json.dumps(payload), payload_sha, datetime.utcnow()))
    conn.commit()
    return payload_sha