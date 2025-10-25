#!/usr/bin/env python3
"""
Metrics streaming for BYOC Connector.
"""

import logging
from typing import Dict, List, Any
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class MetricsStreamer:
    """Handles metrics collection and forwarding to Insight Engine."""
    
    def __init__(self, prom_url: str, control_plane_url: str, simulate: bool = False):
        self.prom_url = prom_url
        self.control_plane_url = control_plane_url
        self.simulate = simulate
        self.metrics_sent = 0
    
    async def collect_metrics(self) -> List[Dict[str, Any]]:
        """Collect metrics from local Prometheus."""
        if self.simulate:
            logger.info("SIMULATION: Collecting mock metrics")
            return [
                {
                    "metric": "cpu_usage_percent",
                    "value": 45.2,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "labels": {"instance": "node-1", "job": "kubernetes-nodes"}
                },
                {
                    "metric": "memory_usage_percent", 
                    "value": 67.8,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "labels": {"instance": "node-1", "job": "kubernetes-nodes"}
                },
                {
                    "metric": "disk_usage_percent",
                    "value": 23.1,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "labels": {"instance": "node-1", "job": "kubernetes-nodes"}
                }
            ]
        
        if not self.prom_url:
            logger.warning("PROM_URL not set, using simulation mode")
            return await self.collect_metrics()  # Recursive call with simulation
        
        try:
            # Query key metrics from Prometheus
            queries = [
                "100 - (avg(irate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)",
                "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
                "(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100"
            ]
            
            metrics = []
            for i, query in enumerate(queries):
                response = requests.get(
                    f"{self.prom_url}/api/v1/query",
                    params={"query": query},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "success" and data["data"]["result"]:
                        result = data["data"]["result"][0]
                        metric_names = ["cpu_usage_percent", "memory_usage_percent", "disk_usage_percent"]
                        
                        metrics.append({
                            "metric": metric_names[i],
                            "value": float(result["value"][1]),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "labels": result.get("metric", {})
                        })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
            # Fallback to simulation
            return await self.collect_metrics()
    
    async def stream_metrics(self, cluster_id: str):
        """Stream metrics to Insight Engine."""
        try:
            metrics = await self.collect_metrics()
            
            if not metrics:
                logger.warning("No metrics collected")
                return
            
            # Format for Insight Engine
            signal_data = {
                "source": f"byoc-{cluster_id}",
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cluster_id": cluster_id
            }
            
            if self.simulate:
                logger.info(f"SIMULATION: Streaming {len(metrics)} metrics for cluster {cluster_id}")
                self.metrics_sent += len(metrics)
                return
            
            # Send to Insight Engine
            response = requests.post(
                f"{self.control_plane_url.replace('8004', '8002')}/signals",
                json=signal_data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.metrics_sent += len(metrics)
                logger.info(f"Streamed {len(metrics)} metrics successfully")
            else:
                logger.error(f"Metrics streaming failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Metrics streaming error: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics streaming summary."""
        return {
            "total_metrics_sent": self.metrics_sent,
            "prom_url": self.prom_url,
            "simulation_mode": self.simulate,
            "last_collection": datetime.now(timezone.utc).isoformat()
        }