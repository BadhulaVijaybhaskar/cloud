"""
Insight Engine - Anomaly detection service for ATOM Cloud
Queries Prometheus metrics and computes anomaly signals
"""

import os
import json
import uuid
import sqlite3
import logging
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

logger = logging.getLogger(__name__)

app = FastAPI(title="ATOM Insight Engine", version="1.0.0")

# Configuration
POSTGRES_DSN = os.getenv("POSTGRES_DSN")
PROM_URL = os.getenv("PROM_URL", "http://localhost:9090")

class ProbeRequest(BaseModel):
    query: str
    threshold: float = 2.0
    lookback_minutes: int = 60

class SignalResponse(BaseModel):
    signal_id: str
    score: float
    metric: str
    value: float
    hint: str

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
    
    # SQLite fallback
    if _sqlite_conn is None:
        _sqlite_conn = sqlite3.connect("insight_signals.db", check_same_thread=False)
        _sqlite_conn.execute("""
            CREATE TABLE IF NOT EXISTS insight_signals (
                id TEXT PRIMARY KEY,
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                score REAL NOT NULL,
                hint TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        _sqlite_conn.commit()
    
    return _sqlite_conn, "sqlite"

def query_prometheus(query: str, lookback_minutes: int = 60) -> List[Dict[str, Any]]:
    """Query Prometheus for metric data"""
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=lookback_minutes)
        
        # Prometheus range query
        params = {
            'query': query,
            'start': start_time.isoformat() + 'Z',
            'end': end_time.isoformat() + 'Z',
            'step': '1m'
        }
        
        response = requests.get(f"{PROM_URL}/api/v1/query_range", params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data['status'] != 'success':
            raise Exception(f"Prometheus query failed: {data.get('error', 'Unknown error')}")
        
        # Extract time series data
        results = []
        for result in data['data']['result']:
            metric_name = result['metric'].get('__name__', query)
            values = [(float(ts), float(val)) for ts, val in result['values']]
            results.append({
                'metric': metric_name,
                'labels': result['metric'],
                'values': values
            })
        
        return results
        
    except requests.RequestException as e:
        logger.warning(f"Prometheus query failed: {e}")
        # Return mock data for testing when Prometheus unavailable
        return [{
            'metric': query,
            'labels': {'__name__': query},
            'values': [(datetime.utcnow().timestamp(), 1.0)]
        }]
    except Exception as e:
        logger.error(f"Prometheus query error: {e}")
        return []

def compute_z_score(values: List[float], current_value: float) -> float:
    """Compute z-score for anomaly detection"""
    if len(values) < 2:
        return 0.0
    
    try:
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        
        if stdev == 0:
            return 0.0
        
        z_score = abs(current_value - mean) / stdev
        return z_score
        
    except Exception as e:
        logger.error(f"Z-score calculation error: {e}")
        return 0.0

def compute_ewma_score(values: List[float], alpha: float = 0.3) -> float:
    """Compute EWMA-based anomaly score"""
    if len(values) < 2:
        return 0.0
    
    try:
        # Calculate EWMA
        ewma = values[0]
        for value in values[1:]:
            ewma = alpha * value + (1 - alpha) * ewma
        
        # Current value vs EWMA
        current_value = values[-1]
        deviation = abs(current_value - ewma)
        
        # Normalize by historical variance
        variance = statistics.variance(values) if len(values) > 1 else 1.0
        score = deviation / (variance ** 0.5) if variance > 0 else 0.0
        
        return score
        
    except Exception as e:
        logger.error(f"EWMA calculation error: {e}")
        return 0.0

def store_signal(metric: str, value: float, score: float, hint: str) -> str:
    """Store anomaly signal in database"""
    signal_id = str(uuid.uuid4())
    conn, db_type = get_db_connection()
    
    try:
        if db_type == "postgres":
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO insight_signals (id, metric, value, score, hint)
                VALUES (%s, %s, %s, %s, %s)
            """, (signal_id, metric, value, score, hint))
        else:  # sqlite
            conn.execute("""
                INSERT INTO insight_signals (id, metric, value, score, hint)
                VALUES (?, ?, ?, ?, ?)
            """, (signal_id, metric, value, score, hint))
            conn.commit()
        
        logger.info(f"Stored signal {signal_id} for metric {metric}")
        return signal_id
        
    except Exception as e:
        logger.error(f"Failed to store signal: {e}")
        raise
    finally:
        if db_type == "postgres":
            conn.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "prometheus_url": PROM_URL
    }

@app.post("/probe", response_model=SignalResponse)
async def probe_metrics(request: ProbeRequest):
    """
    Probe Prometheus metrics for anomalies
    
    Queries Prometheus, computes anomaly scores, and stores signals if threshold exceeded
    """
    try:
        # Query Prometheus
        prom_results = query_prometheus(request.query, request.lookback_minutes)
        
        if not prom_results:
            raise HTTPException(status_code=400, detail="No data returned from Prometheus")
        
        # Process each time series
        signals = []
        for result in prom_results:
            metric_name = result['metric']
            values = [val for ts, val in result['values']]
            
            if not values:
                continue
            
            current_value = values[-1]
            
            # Compute anomaly scores
            z_score = compute_z_score(values, current_value)
            ewma_score = compute_ewma_score(values)
            
            # Use maximum score
            max_score = max(z_score, ewma_score)
            
            # Check threshold
            if max_score >= request.threshold:
                # Generate hint
                hint = f"Anomaly detected: z-score={z_score:.2f}, ewma-score={ewma_score:.2f}"
                if z_score > ewma_score:
                    hint += " (statistical outlier)"
                else:
                    hint += " (trend deviation)"
                
                # Store signal
                signal_id = store_signal(metric_name, current_value, max_score, hint)
                
                signals.append(SignalResponse(
                    signal_id=signal_id,
                    score=max_score,
                    metric=metric_name,
                    value=current_value,
                    hint=hint
                ))
        
        if signals:
            return signals[0]  # Return first signal for now
        else:
            # No anomaly detected
            return SignalResponse(
                signal_id="",
                score=max_score if 'max_score' in locals() else 0.0,
                metric=request.query,
                value=current_value if 'current_value' in locals() else 0.0,
                hint="No anomaly detected"
            )
            
    except Exception as e:
        logger.error(f"Probe failed: {e}")
        raise HTTPException(status_code=500, detail=f"Probe failed: {str(e)}")

@app.get("/signals")
async def get_signals(limit: int = 50, metric: Optional[str] = None):
    """Get recent anomaly signals"""
    conn, db_type = get_db_connection()
    
    try:
        if db_type == "postgres":
            cursor = conn.cursor()
            if metric:
                cursor.execute("""
                    SELECT id, metric, value, score, hint, created_at
                    FROM insight_signals 
                    WHERE metric = %s
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (metric, limit))
            else:
                cursor.execute("""
                    SELECT id, metric, value, score, hint, created_at
                    FROM insight_signals 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
            results = cursor.fetchall()
        else:  # sqlite
            if metric:
                cursor = conn.execute("""
                    SELECT id, metric, value, score, hint, created_at
                    FROM insight_signals 
                    WHERE metric = ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (metric, limit))
            else:
                cursor = conn.execute("""
                    SELECT id, metric, value, score, hint, created_at
                    FROM insight_signals 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
            results = cursor.fetchall()
        
        signals = []
        for row in results:
            signals.append({
                "id": row[0],
                "metric": row[1],
                "value": row[2],
                "score": row[3],
                "hint": row[4],
                "created_at": row[5]
            })
        
        return {
            "signals": signals,
            "total": len(signals)
        }
        
    except Exception as e:
        logger.error(f"Failed to get signals: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get signals: {str(e)}")
    finally:
        if db_type == "postgres":
            conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)