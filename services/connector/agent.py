#!/usr/bin/env python3
"""
NeuralOps BYOC Connector Agent
Lightweight agent for external Kubernetes clusters.
"""

import os
import json
import logging
import asyncio
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from auth import VaultAuth
from metrics import MetricsStreamer
from executor import WPKExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectorConfig:
    """Configuration for BYOC Connector."""
    
    def __init__(self):
        self.cluster_id = os.getenv("CLUSTER_ID", f"cluster-{uuid.uuid4().hex[:8]}")
        self.control_plane_url = os.getenv("CONTROL_PLANE_URL", "http://localhost:8004")
        self.vault_addr = os.getenv("VAULT_ADDR", "")
        self.prom_url = os.getenv("PROM_URL", "http://localhost:9090")
        self.cosign_key = os.getenv("COSIGN_KEY", "")
        self.simulate = os.getenv("SIMULATE", "true").lower() == "true"

class ExecutionRequest(BaseModel):
    playbook_id: str
    signature: str
    payload: Dict[str, Any]
    orchestration_id: str

class HealthStatus(BaseModel):
    cluster_id: str
    status: str
    timestamp: str
    metrics_count: int = 0
    last_execution: Optional[str] = None

class BYOCConnector:
    """Main BYOC Connector agent."""
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.auth = VaultAuth(config.vault_addr, config.simulate)
        self.metrics = MetricsStreamer(config.prom_url, config.control_plane_url, config.simulate)
        self.executor = WPKExecutor(config.cosign_key, config.simulate)
        self.registered = False
        self.last_execution = None
        
    async def register_cluster(self) -> bool:
        """Register cluster with NeuralOps control plane."""
        try:
            # Get Vault token
            vault_token = await self.auth.get_token()
            
            registration_data = {
                "cluster_id": self.config.cluster_id,
                "hostname": os.getenv("HOSTNAME", "localhost"),
                "labels": {
                    "environment": os.getenv("ENV", "development"),
                    "region": os.getenv("REGION", "local")
                },
                "capabilities": ["metrics", "execution", "audit"]
            }
            
            if self.config.simulate:
                logger.info(f"SIMULATION: Registering cluster {self.config.cluster_id}")
                self.registered = True
                return True
            
            response = requests.post(
                f"{self.config.control_plane_url}/register",
                json=registration_data,
                headers={"Authorization": f"Bearer {vault_token}"},
                timeout=30
            )
            
            if response.status_code == 200:
                self.registered = True
                logger.info(f"Cluster {self.config.cluster_id} registered successfully")
                return True
            else:
                logger.error(f"Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            if self.config.simulate:
                self.registered = True
                return True
            return False
    
    async def start_metrics_streaming(self):
        """Start metrics streaming loop."""
        while True:
            try:
                if self.registered:
                    await self.metrics.stream_metrics(self.config.cluster_id)
                await asyncio.sleep(30)  # Stream every 30 seconds
            except Exception as e:
                logger.error(f"Metrics streaming error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute
    
    async def send_heartbeat(self):
        """Send periodic heartbeat to control plane."""
        while True:
            try:
                if self.registered:
                    health_data = HealthStatus(
                        cluster_id=self.config.cluster_id,
                        status="healthy",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        metrics_count=self.metrics.metrics_sent,
                        last_execution=self.last_execution
                    )
                    
                    if self.config.simulate:
                        logger.info(f"SIMULATION: Heartbeat sent for {self.config.cluster_id}")
                    else:
                        response = requests.put(
                            f"{self.config.control_plane_url}/healthz",
                            json=health_data.dict(),
                            timeout=10
                        )
                        logger.info(f"Heartbeat sent: {response.status_code}")
                
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(60)
    
    async def execute_wpk(self, request: ExecutionRequest) -> Dict[str, Any]:
        """Execute signed WPK payload."""
        try:
            # Verify signature
            if not await self.executor.verify_signature(request.signature, request.payload):
                raise HTTPException(status_code=403, detail="Invalid signature")
            
            # Execute playbook
            result = await self.executor.execute(request.playbook_id, request.payload)
            
            self.last_execution = datetime.now(timezone.utc).isoformat()
            
            # Log execution
            await self.executor.log_execution(
                request.orchestration_id,
                request.playbook_id,
                result
            )
            
            return {
                "status": "success",
                "execution_id": result.get("execution_id"),
                "cluster_id": self.config.cluster_id,
                "timestamp": self.last_execution
            }
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "cluster_id": self.config.cluster_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

# FastAPI app for receiving commands
app = FastAPI(title="BYOC Connector", version="1.0.0")
connector = None

@app.post("/execute")
async def execute_endpoint(request: ExecutionRequest):
    """Receive and execute WPK from orchestrator."""
    if not connector or not connector.registered:
        raise HTTPException(status_code=503, detail="Connector not registered")
    
    return await connector.execute_wpk(request)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if connector and connector.registered else "not_registered",
        "cluster_id": connector.config.cluster_id if connector else "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

async def main():
    """Main connector loop."""
    global connector
    
    config = ConnectorConfig()
    connector = BYOCConnector(config)
    
    logger.info(f"Starting BYOC Connector for cluster: {config.cluster_id}")
    logger.info(f"Simulation mode: {config.simulate}")
    
    # Register cluster
    if not await connector.register_cluster():
        logger.error("Failed to register cluster")
        return
    
    # Start background tasks
    tasks = [
        asyncio.create_task(connector.start_metrics_streaming()),
        asyncio.create_task(connector.send_heartbeat())
    ]
    
    # Start FastAPI server
    server_config = uvicorn.Config(app, host="0.0.0.0", port=8005, log_level="info")
    server = uvicorn.Server(server_config)
    
    try:
        await asyncio.gather(
            server.serve(),
            *tasks
        )
    except KeyboardInterrupt:
        logger.info("Shutting down connector...")
        for task in tasks:
            task.cancel()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BYOC Connector Agent")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode")
    args = parser.parse_args()
    
    if args.simulate:
        os.environ["SIMULATE"] = "true"
    
    asyncio.run(main())