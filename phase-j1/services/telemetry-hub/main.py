#!/usr/bin/env python3
"""
J.1.3 Telemetry Hub - Production observability and monitoring
"""

from fastapi import FastAPI, Request
import os, json, time, random, logging

app = FastAPI(title="Telemetry Hub", version="1.0.0")
logger = logging.getLogger("telemetry-hub")
logging.basicConfig(level=logging.INFO)

# Global state
metrics_store = {}
traces = {}
logs = []
simulation_mode = os.getenv("SIMULATION_MODE", "true").lower() == "true"

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "telemetry-hub",
        "simulation_mode": simulation_mode,
        "metrics_count": len(metrics_store),
        "traces_count": len(traces),
        "logs_count": len(logs)
    }

@app.get("/metrics")
async def metrics():
    """P19: Live Observability - Prometheus metrics endpoint"""
    if simulation_mode:
        # Generate synthetic metrics
        return {
            "telemetry_metrics_received_total": len(metrics_store),
            "telemetry_traces_received_total": len(traces),
            "telemetry_logs_received_total": len(logs),
            "telemetry_processing_duration_seconds": round(random.uniform(0.001, 0.1), 3)
        }
    else:
        # In production, would return actual Prometheus metrics
        return {"note": "Production metrics integration not implemented"}

@app.post("/v1/metrics")
async def ingest_metrics(request: Request):
    """Ingest metrics from services"""
    body = await request.json()
    
    timestamp = time.time()
    service_name = body.get("service", "unknown")
    
    if service_name not in metrics_store:
        metrics_store[service_name] = []
    
    metric_entry = {
        "timestamp": timestamp,
        "metrics": body.get("metrics", {}),
        "labels": body.get("labels", {})
    }
    
    metrics_store[service_name].append(metric_entry)
    
    # Keep only last 1000 entries per service
    if len(metrics_store[service_name]) > 1000:
        metrics_store[service_name] = metrics_store[service_name][-1000:]
    
    logger.info(f"Ingested metrics from {service_name}")
    
    return {"status": "accepted", "timestamp": timestamp}

@app.post("/v1/traces")
async def ingest_traces(request: Request):
    """Ingest OpenTelemetry traces"""
    body = await request.json()
    
    trace_id = body.get("trace_id", f"trace_{int(time.time())}")
    
    traces[trace_id] = {
        "trace_id": trace_id,
        "spans": body.get("spans", []),
        "timestamp": time.time(),
        "service": body.get("service", "unknown")
    }
    
    # Keep only last 500 traces
    if len(traces) > 500:
        oldest_trace = min(traces.keys(), key=lambda k: traces[k]["timestamp"])
        del traces[oldest_trace]
    
    logger.info(f"Ingested trace {trace_id}")
    
    return {"status": "accepted", "trace_id": trace_id}

@app.post("/v1/logs")
async def ingest_logs(request: Request):
    """Ingest structured logs"""
    body = await request.json()
    
    log_entry = {
        "timestamp": time.time(),
        "level": body.get("level", "INFO"),
        "message": body.get("message", ""),
        "service": body.get("service", "unknown"),
        "metadata": body.get("metadata", {})
    }
    
    logs.append(log_entry)
    
    # Keep only last 10000 log entries
    if len(logs) > 10000:
        logs[:] = logs[-10000:]
    
    return {"status": "accepted"}

@app.get("/v1/metrics/{service_name}")
async def get_service_metrics(service_name: str):
    """Get metrics for specific service"""
    if service_name not in metrics_store:
        return {"metrics": [], "service": service_name}
    
    return {
        "service": service_name,
        "metrics": metrics_store[service_name][-100:],  # Last 100 entries
        "count": len(metrics_store[service_name])
    }

@app.get("/v1/traces/{trace_id}")
async def get_trace(trace_id: str):
    """Get specific trace"""
    if trace_id not in traces:
        return {"error": "Trace not found"}
    
    return traces[trace_id]

@app.get("/v1/dashboard")
async def get_dashboard_data():
    """Get dashboard data for observability"""
    if simulation_mode:
        # Generate synthetic dashboard data
        return {
            "services": list(metrics_store.keys()),
            "total_metrics": len(metrics_store),
            "total_traces": len(traces),
            "total_logs": len(logs),
            "system_health": {
                "cpu_usage": round(random.uniform(0.3, 0.8), 2),
                "memory_usage": round(random.uniform(0.4, 0.9), 2),
                "disk_usage": round(random.uniform(0.2, 0.7), 2)
            },
            "slo_status": {
                "availability": round(random.uniform(0.995, 0.999), 4),
                "latency_p95": round(random.uniform(100, 500), 1),
                "error_rate": round(random.uniform(0.001, 0.01), 4)
            },
            "simulation_mode": True
        }
    else:
        return {"note": "Production dashboard not implemented"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10003)