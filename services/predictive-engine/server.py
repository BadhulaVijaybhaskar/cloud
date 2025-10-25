#!/usr/bin/env python3
"""
Predictive Intelligence Engine Server
FastAPI service for failure prediction and RCA recommendations
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import sqlite3
import uuid

from fastapi import FastAPI, HTTPException
import uvicorn
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from model import PredictiveModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
predictions_total = Counter('predictions_total', 'Total predictions made', ['model_version', 'risk_level'])
prediction_duration = Histogram('prediction_duration_seconds', 'Prediction processing time')

app = FastAPI(title="Predictive Intelligence Engine", version="1.0.0")

class PredictiveEngine:
    """Main predictive engine service"""
    
    def __init__(self):
        self.db_path = "predictions.db"
        self.model = PredictiveModel()
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id TEXT PRIMARY KEY,
                    run_id TEXT,
                    signal_id TEXT,
                    model_version TEXT NOT NULL,
                    probability REAL NOT NULL CHECK (probability >= 0 AND probability <= 1),
                    recommendation TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_run_id ON predictions(run_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at DESC)")
    
    def predict(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate prediction and store result"""
        prediction_id = str(uuid.uuid4())
        
        with prediction_duration.time():
            # Get prediction from model
            result = self.model.predict(request_data.get('metrics_data', {}))
            
            # Store prediction
            prediction = {
                'id': prediction_id,
                'run_id': request_data.get('run_id'),
                'signal_id': request_data.get('signal_id'),
                'model_version': result['model_version'],
                'probability': result['probability'],
                'recommendation': json.dumps(result['recommendations']),
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            self._save_prediction(prediction)
            
            # Update metrics
            risk_level = result['recommendations'].get('risk_level', 'unknown')
            predictions_total.labels(
                model_version=result['model_version'],
                risk_level=risk_level
            ).inc()
            
            return {
                'id': prediction_id,
                'probability': result['probability'],
                'model_version': result['model_version'],
                'recommendations': result['recommendations'],
                'created_at': prediction['created_at']
            }
    
    def _save_prediction(self, prediction: Dict[str, Any]):
        """Save prediction to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO predictions 
                (id, run_id, signal_id, model_version, probability, recommendation, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction['id'], prediction['run_id'], prediction['signal_id'],
                prediction['model_version'], prediction['probability'],
                prediction['recommendation'], prediction['created_at']
            ))
    
    def get_predictions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent predictions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM predictions 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            predictions = []
            for row in cursor:
                prediction = dict(row)
                if prediction['recommendation']:
                    prediction['recommendation'] = json.loads(prediction['recommendation'])
                predictions.append(prediction)
            
            return predictions

# Global engine instance
engine = PredictiveEngine()

@app.post("/predict")
async def predict_endpoint(request: Dict[str, Any]):
    """Generate failure prediction and recommendations"""
    try:
        return engine.predict(request)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predictions")
async def get_predictions(limit: int = 50):
    """Get recent predictions"""
    try:
        return {"predictions": engine.get_predictions(limit)}
    except Exception as e:
        logger.error(f"Failed to get predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_trained": engine.model.is_trained,
        "model_version": engine.model.version,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import Response
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)