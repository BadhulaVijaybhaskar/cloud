#!/usr/bin/env python3
"""
ATOM Marketplace Worker
Background job processor for marketplace operations
"""

import asyncio
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
BILLING_SERVICE_URL = os.getenv('BILLING_SERVICE_URL', 'http://localhost:8200')

class MarketplaceWorker:
    def __init__(self):
        self.job_queue = []
        self.processed_jobs = {}
        
    async def process_publish_job(self, job: Dict[str, Any]):
        """Process model/agent publish job"""
        
        job_id = job["job_id"]
        model_data = job["model"]
        
        print(f"Processing publish job {job_id} for {model_data['name']}")
        
        # Simulate artifact processing
        if SIMULATION_MODE:
            # Simulate S3 upload
            artifact_path = f"s3://atom-models-sim/{model_data['vendor_id']}/{model_data['name']}/{model_data['version']}/artifact.tar.gz"
            checksum = hashlib.sha256(f"{model_data['name']}{model_data['version']}".encode()).hexdigest()
            
            # Simulate governance checks
            governance_result = {
                "p1_pii_scan": "PASS",
                "p5_bias_check": "PASS", 
                "security_scan": "PASS",
                "license_validation": "PASS"
            }
            
            # Simulate registry registration
            await asyncio.sleep(1)  # Simulate processing time
            
            result = {
                "job_id": job_id,
                "status": "completed",
                "artifact_path": artifact_path,
                "checksum": checksum,
                "governance_result": governance_result,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        else:
            # Real processing would happen here
            result = {"job_id": job_id, "status": "failed", "error": "Real processing not implemented"}
        
        self.processed_jobs[job_id] = result
        
        # Emit billing event
        await self.emit_billing_event({
            "event_type": "model_published",
            "model_id": job_id,
            "vendor_id": model_data["vendor_id"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        print(f"Completed job {job_id}: {result['status']}")
        return result
    
    async def emit_billing_event(self, event: Dict[str, Any]):
        """Emit billing event to billing service"""
        
        if SIMULATION_MODE:
            print(f"📊 Billing event (simulated): {json.dumps(event)}")
            
            # Write to reports for verification
            with open("reports/marketplace_billing_events.jsonl", "a") as f:
                f.write(json.dumps(event) + "\n")
        else:
            # Real HTTP call to billing service
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(f"{BILLING_SERVICE_URL}/v1/events", json=event)
    
    async def process_usage_event(self, usage: Dict[str, Any]):
        """Process model/agent usage for billing"""
        
        billing_event = {
            "project_id": usage.get("project_id"),
            "model_id": usage.get("model_id"),
            "units": usage.get("units", 1),
            "cost_center": usage.get("cost_center", "default"),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "usage_metered"
        }
        
        await self.emit_billing_event(billing_event)
    
    async def run_worker(self):
        """Main worker loop"""
        
        print(f"🚀 Marketplace Worker started (SIMULATION_MODE={SIMULATION_MODE})")
        
        while True:
            if self.job_queue:
                job = self.job_queue.pop(0)
                await self.process_publish_job(job)
            
            await asyncio.sleep(1)  # Check for jobs every second
    
    def enqueue_job(self, job: Dict[str, Any]):
        """Add job to processing queue"""
        self.job_queue.append(job)
        print(f"📥 Enqueued job {job['job_id']}")

# Global worker instance
worker = MarketplaceWorker()

async def main():
    """Main entry point"""
    
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    
    # Start worker
    await worker.run_worker()

if __name__ == "__main__":
    asyncio.run(main())