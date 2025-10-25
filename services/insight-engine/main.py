#!/usr/bin/env python3
"""
NeuralOps Insight Engine - Anomaly Detection and Signal Generation
Detects anomalies in metrics and produces actionable signals.
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import requests
import numpy as np
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
signals_total = Counter('neuralops_signals_total', 'Total signals generated', ['type', 'severity'])
anomaly_total = Counter('neuralops_anomaly_total', 'Total anomalies detected', ['method'])
analyze_duration = Histogram('neuralops_analyze_duration_seconds', 'Analysis duration')

app = FastAPI(title="NeuralOps Insight Engine", version="1.0.0")

class AnalyzeRequest(BaseModel):
    query: str
    lookback: str = "5m"
    labels: Dict[str, str] = {}

class AnalyzeResponse(BaseModel):
    score: float
    method: str
    hint: str
    timestamp: str

class InsightEngine:
    """Core insight engine for anomaly detection."""
    
    def __init__(self):
        self.prom_url = os.getenv("PROM_URL", "http://localhost:9090")
        self.db_path = "insight_signals.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for signals."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS insight_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    query TEXT NOT NULL,
                    score REAL NOT NULL,
                    method TEXT NOT NULL,
                    hint TEXT NOT NULL,
                    labels TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    async def analyze_metric(self, request: AnalyzeRequest) -> AnalyzeResponse:
        """Analyze metric for anomalies."""
        with analyze_duration.time():
            try:
                # Query Prometheus
                data = await self._query_prometheus(request.query, request.lookback)
                
                if not data:
                    return AnalyzeResponse(
                        score=0.0,
                        method="no_data",
                        hint="No data available for analysis",
                        timestamp=datetime.utcnow().isoformat()
                    )
                
                # Perform anomaly detection
                score, method, hint = self._detect_anomaly(data)
                
                # Record metrics
                anomaly_total.labels(method=method).inc()
                
                return AnalyzeResponse(
                    score=score,
                    method=method,
                    hint=hint,
                    timestamp=datetime.utcnow().isoformat()
                )
                
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _query_prometheus(self, query: str, lookback: str) -> List[float]:
        """Query Prometheus for metric data."""
        try:
            # Use synthetic data if Prometheus not available
            if not self._is_prometheus_available():
                logger.warning("Prometheus not available, using synthetic data")
                return self._generate_synthetic_data()
            
            # Real Prometheus query
            params = {
                'query': query,
                'start': (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                'end': datetime.utcnow().isoformat(),
                'step': '1m'
            }
            
            response = requests.get(f"{self.prom_url}/api/v1/query_range", params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result['status'] != 'success':
                return []
            
            # Extract values
            values = []
            for series in result['data']['result']:
                for timestamp, value in series['values']:
                    try:
                        values.append(float(value))
                    except (ValueError, TypeError):
                        continue
            
            return values
            
        except Exception as e:
            logger.warning(f"Prometheus query failed: {e}, using synthetic data")
            return self._generate_synthetic_data()
    
    def _is_prometheus_available(self) -> bool:
        """Check if Prometheus is available."""
        try:
            response = requests.get(f"{self.prom_url}/api/v1/status/config", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _generate_synthetic_data(self) -> List[float]:
        """Generate synthetic metric data for testing."""
        # Generate 30 data points with some anomalies
        np.random.seed(42)
        base_values = np.random.normal(100, 10, 25)  # Normal values
        anomaly_values = np.random.normal(200, 20, 5)  # Anomalous values
        return np.concatenate([base_values, anomaly_values]).tolist()
    
    def _detect_anomaly(self, data: List[float]) -> tuple[float, str, str]:
        """Detect anomalies in metric data."""
        if len(data) < 3:
            return 0.0, "insufficient_data", "Not enough data points for analysis"
        
        values = np.array(data)
        
        # Z-score method
        z_scores = np.abs(stats.zscore(values))
        max_z_score = np.max(z_scores)
        
        if max_z_score > 3.0:
            score = min(1.0, max_z_score / 5.0)  # Normalize to 0-1
            return score, "zscore", f"High z-score detected: {max_z_score:.2f}"
        
        # EWMA method for trend detection
        ewma = self._calculate_ewma(values)
        recent_avg = np.mean(values[-5:]) if len(values) >= 5 else np.mean(values)
        ewma_deviation = abs(recent_avg - ewma) / ewma if ewma > 0 else 0
        
        if ewma_deviation > 0.3:  # 30% deviation
            score = min(1.0, ewma_deviation)
            return score, "ewma", f"Trend deviation detected: {ewma_deviation:.2f}"
        
        return 0.1, "normal", "No significant anomaly detected"
    
    def _calculate_ewma(self, values: np.ndarray, alpha: float = 0.3) -> float:
        """Calculate Exponentially Weighted Moving Average."""
        ewma = values[0]
        for value in values[1:]:
            ewma = alpha * value + (1 - alpha) * ewma
        return ewma
    
    def store_signal(self, signal_type: str, severity: str, query: str, 
                    score: float, method: str, hint: str, labels: Dict[str, str] = None):
        """Store signal in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO insight_signals 
                    (timestamp, signal_type, severity, query, score, method, hint, labels)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.utcnow().isoformat(),
                    signal_type,
                    severity,
                    query,
                    score,
                    method,
                    hint,
                    json.dumps(labels or {})
                ))
            
            # Record metrics
            signals_total.labels(type=signal_type, severity=severity).inc()
            logger.info(f"Signal stored: {signal_type} ({severity}) - {hint}")
            
        except Exception as e:
            logger.error(f"Failed to store signal: {e}")

# Global engine instance
engine = InsightEngine()

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_endpoint(request: AnalyzeRequest):
    """Analyze metric for anomalies."""
    return await engine.analyze_metric(request)

@app.get("/signals")
async def get_signals(limit: int = 10):
    """Get recent signals."""
    try:
        with sqlite3.connect(engine.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM insight_signals 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            signals = []
            for row in cursor:
                signal = dict(row)
                signal['labels'] = json.loads(signal['labels'])
                signals.append(signal)
            
            return {"signals": signals}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "prometheus_available": engine._is_prometheus_available(),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import Response
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

async def periodic_analysis():
    """Periodic worker to analyze predefined queries."""
    queries = [
        "rate(http_requests_total[5m])",
        "cpu_usage_percent",
        "memory_usage_percent",
        "disk_usage_percent"
    ]
    
    while True:
        try:
            for query in queries:
                request = AnalyzeRequest(query=query, lookback="5m")
                result = await engine.analyze_metric(request)
                
                # Store significant signals
                if result.score > 0.5:
                    severity = "critical" if result.score > 0.8 else "warning"
                    engine.store_signal(
                        signal_type="anomaly",
                        severity=severity,
                        query=query,
                        score=result.score,
                        method=result.method,
                        hint=result.hint
                    )
            
            await asyncio.sleep(60)  # Run every minute
            
        except Exception as e:
            logger.error(f"Periodic analysis failed: {e}")
            await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    """Start background tasks."""
    asyncio.create_task(periodic_analysis())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)