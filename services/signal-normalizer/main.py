#!/usr/bin/env python3
"""
Phase I.5 - Signal Normalizer
Normalizes and validates signals against schemas
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
SIGNALS_NORMALIZED = Counter('signals_normalized_total', 'Total signals normalized')
NORMALIZATION_ERRORS = Counter('normalization_errors_total', 'Total normalization errors')
NORMALIZATION_LATENCY = Histogram('normalization_latency_seconds', 'Normalization latency')

app = FastAPI(title="Signal Normalizer", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

class NormalizeRequest(BaseModel):
    signals: List[Dict[str, Any]]
    target_schema: str = "SignalV1"

def validate_signal_v1(signal: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize signal to SignalV1 format"""
    required_fields = ['signal_id', 'timestamp', 'source', 'signal_type', 'data']
    
    # Check required fields
    for field in required_fields:
        if field not in signal:
            raise ValueError(f"Missing required field: {field}")
    
    # Normalize timestamp
    if not signal['timestamp'].endswith('Z'):
        signal['timestamp'] = signal['timestamp'] + 'Z'
    
    # Ensure metadata exists
    if 'metadata' not in signal:
        signal['metadata'] = {}
    
    # Add normalization metadata
    signal['metadata']['normalized_at'] = datetime.utcnow().isoformat() + 'Z'
    signal['metadata']['normalizer_version'] = '1.0.0'
    
    return signal

def detect_schema_version(signal: Dict[str, Any]) -> str:
    """Auto-detect signal schema version"""
    if 'signal_id' in signal and 'signal_type' in signal:
        return 'SignalV1'
    elif 'id' in signal and 'type' in signal:
        return 'LegacySignal'
    else:
        return 'Unknown'

@app.post("/v1/normalize")
async def normalize_signals(request: NormalizeRequest):
    """Normalize signals to target schema"""
    results = []
    
    for signal in request.signals:
        try:
            with NORMALIZATION_LATENCY.time():
                # Auto-detect schema if not specified
                detected_schema = detect_schema_version(signal)
                
                if request.target_schema == "SignalV1":
                    if detected_schema == "LegacySignal":
                        # Convert legacy format
                        normalized = {
                            'signal_id': signal.get('id', f"sig-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"),
                            'timestamp': signal.get('timestamp', datetime.utcnow().isoformat() + 'Z'),
                            'source': signal.get('source', 'unknown'),
                            'signal_type': signal.get('type', 'event'),
                            'data': signal.get('payload', signal.get('data', {})),
                            'metadata': signal.get('meta', {})
                        }
                    else:
                        normalized = signal.copy()
                    
                    # Validate and normalize
                    normalized = validate_signal_v1(normalized)
                    
                    SIGNALS_NORMALIZED.inc()
                    results.append({
                        'original_id': signal.get('signal_id', signal.get('id')),
                        'normalized_signal': normalized,
                        'status': 'success',
                        'schema_detected': detected_schema,
                        'schema_target': request.target_schema
                    })
                    
                else:
                    raise ValueError(f"Unsupported target schema: {request.target_schema}")
                    
        except Exception as e:
            NORMALIZATION_ERRORS.inc()
            results.append({
                'original_id': signal.get('signal_id', signal.get('id', 'unknown')),
                'status': 'error',
                'error': str(e),
                'schema_detected': detect_schema_version(signal)
            })
    
    return {
        'normalized_count': len([r for r in results if r['status'] == 'success']),
        'error_count': len([r for r in results if r['status'] == 'error']),
        'results': results
    }

@app.post("/v1/validate")
async def validate_signals(signals: List[Dict[str, Any]]):
    """Validate signals against schema without normalization"""
    results = []
    
    for signal in signals:
        try:
            schema = detect_schema_version(signal)
            if schema == "SignalV1":
                validate_signal_v1(signal)
                results.append({
                    'signal_id': signal.get('signal_id'),
                    'status': 'valid',
                    'schema': schema
                })
            else:
                results.append({
                    'signal_id': signal.get('signal_id', signal.get('id')),
                    'status': 'invalid',
                    'schema': schema,
                    'error': 'Unsupported schema version'
                })
        except Exception as e:
            results.append({
                'signal_id': signal.get('signal_id', signal.get('id')),
                'status': 'invalid',
                'error': str(e)
            })
    
    return {
        'valid_count': len([r for r in results if r['status'] == 'valid']),
        'invalid_count': len([r for r in results if r['status'] == 'invalid']),
        'results': results
    }

@app.get("/v1/schemas")
async def list_schemas():
    """List supported schemas"""
    return {
        'schemas': [
            {
                'name': 'SignalV1',
                'version': '1.0.0',
                'description': 'Standard CIN signal format',
                'required_fields': ['signal_id', 'timestamp', 'source', 'signal_type', 'data']
            },
            {
                'name': 'LegacySignal',
                'version': '0.9.0',
                'description': 'Legacy signal format (auto-converted)',
                'required_fields': ['id', 'type', 'payload']
            }
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "signal-normalizer",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return JSONResponse(
        content=generate_latest().decode('utf-8'),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)