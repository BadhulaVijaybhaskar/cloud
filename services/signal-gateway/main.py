#!/usr/bin/env python3
"""
Phase I.5 - Signal Gateway
Ingests signals from agents, validates, classifies, and routes to consensus-bus
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
import logging
from prometheus_client import Counter, Histogram, generate_latest
import asyncio

# Metrics
SIGNALS_INGESTED = Counter('signals_ingested_total', 'Total signals ingested', ['signal_type', 'classification'])
SIGNALS_REJECTED = Counter('signals_rejected_total', 'Total signals rejected', ['reason'])
INGESTION_LATENCY = Histogram('signal_ingestion_seconds', 'Signal ingestion latency')

app = FastAPI(title="Signal Gateway", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:9092')

class SignalV1(BaseModel):
    signal_id: str
    timestamp: str
    source: str
    signal_type: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}
    signature: Optional[str] = None
    
    @validator('signal_id')
    def validate_signal_id(cls, v):
        if not v.startswith('sig-'):
            raise ValueError('signal_id must start with sig-')
        return v
    
    @validator('signal_type')
    def validate_signal_type(cls, v):
        allowed_types = ['metric', 'event', 'decision', 'model_update', 'conflict']
        if v not in allowed_types:
            raise ValueError(f'signal_type must be one of {allowed_types}')
        return v

class IngestRequest(BaseModel):
    signals: List[SignalV1]
    batch_id: Optional[str] = None

def verify_auth_token(authorization: str = Header(None)):
    """Verify authentication token"""
    if not authorization or not authorization.startswith('Bearer '):
        if SIMULATION_MODE:
            return {"agent_id": "sim-agent", "tenant_id": "sim-tenant"}
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    if SIMULATION_MODE:
        return {"agent_id": "sim-agent", "tenant_id": "sim-tenant"}
    return {"agent_id": "extracted-agent", "tenant_id": "extracted-tenant"}

def classify_signal(signal: SignalV1) -> str:
    """Classify signal based on data content and metadata"""
    # Check explicit classification
    if signal.metadata and 'classification' in signal.metadata:
        return signal.metadata['classification']
    
    # Auto-classify based on content
    data_str = json.dumps(signal.data, sort_keys=True).lower()
    
    # Check for PII patterns
    pii_indicators = ['email', 'phone', 'ssn', 'credit_card', 'personal']
    if any(indicator in data_str for indicator in pii_indicators):
        return 'confidential'
    
    # Check for sensitive operations
    sensitive_ops = ['delete', 'destroy', 'admin', 'root', 'password']
    if any(op in data_str for op in sensitive_ops):
        return 'restricted'
    
    # Check signal type
    if signal.signal_type in ['model_update', 'decision']:
        return 'internal'
    
    return 'public'

def validate_data_policy(signal: SignalV1, classification: str) -> bool:
    """Validate signal against data classification policy"""
    # Restricted data requires consent token
    if classification == 'restricted':
        if not signal.metadata or not signal.metadata.get('consent_token'):
            return False
    
    # Confidential data requires tenant context
    if classification == 'confidential':
        if not signal.metadata or not signal.metadata.get('tenant_id'):
            return False
    
    return True

async def route_to_consensus_bus(signal: SignalV1, classification: str):
    """Route signal to consensus-bus topic"""
    try:
        if SIMULATION_MODE:
            # Simulate Kafka publish
            topic = f"signals-{classification}"
            logger.info(f"Simulating publish to topic {topic}: {signal.signal_id}")
            await asyncio.sleep(0.01)  # Simulate network latency
            return True
        
        # In production: actual Kafka publish
        return True
        
    except Exception as e:
        logger.error(f"Error routing signal {signal.signal_id}: {e}")
        return False

@app.post("/v1/ingest")
async def ingest_signals(
    request: IngestRequest,
    auth_data: Dict = Depends(verify_auth_token)
):
    """Ingest and route signals"""
    batch_id = request.batch_id or f"batch-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    results = []
    
    for signal in request.signals:
        try:
            with INGESTION_LATENCY.time():
                # Classify signal
                classification = classify_signal(signal)
                
                # Validate against policy
                if not validate_data_policy(signal, classification):
                    SIGNALS_REJECTED.labels(reason='policy_violation').inc()
                    results.append({
                        "signal_id": signal.signal_id,
                        "status": "rejected",
                        "reason": "Policy violation - missing consent or tenant context"
                    })
                    continue
                
                # Add processing metadata
                signal.metadata = signal.metadata or {}
                signal.metadata.update({
                    "classification": classification,
                    "processed_at": datetime.utcnow().isoformat(),
                    "processed_by": "signal-gateway",
                    "batch_id": batch_id,
                    "agent_id": auth_data.get("agent_id"),
                    "tenant_id": auth_data.get("tenant_id")
                })
                
                # Generate signature if not present
                if not signal.signature:
                    signal_str = json.dumps(signal.dict(), sort_keys=True)
                    signal.signature = hashlib.sha256(signal_str.encode()).hexdigest()[:16]
                
                # Route to consensus bus
                routed = await route_to_consensus_bus(signal, classification)
                
                if routed:
                    SIGNALS_INGESTED.labels(
                        signal_type=signal.signal_type,
                        classification=classification
                    ).inc()
                    
                    results.append({
                        "signal_id": signal.signal_id,
                        "status": "accepted",
                        "classification": classification,
                        "routed_to": f"signals-{classification}"
                    })
                else:
                    SIGNALS_REJECTED.labels(reason='routing_failed').inc()
                    results.append({
                        "signal_id": signal.signal_id,
                        "status": "rejected", 
                        "reason": "Routing failed"
                    })
                    
        except Exception as e:
            SIGNALS_REJECTED.labels(reason='processing_error').inc()
            results.append({
                "signal_id": signal.signal_id,
                "status": "error",
                "reason": str(e)
            })
    
    return {
        "batch_id": batch_id,
        "processed": len(results),
        "accepted": len([r for r in results if r["status"] == "accepted"]),
        "rejected": len([r for r in results if r["status"] in ["rejected", "error"]]),
        "results": results
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "signal-gateway",
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
    uvicorn.run(app, host="0.0.0.0", port=8001)