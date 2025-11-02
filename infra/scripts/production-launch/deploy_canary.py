#!/usr/bin/env python3
"""
Phase J.1 Canary Deployment Script
"""

import os, json, time, subprocess, requests, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deploy_canary")

def run_command(cmd, timeout=120):
    """Run shell command with timeout"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_service_health(url, timeout=30):
    """Check if service is healthy"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.ok:
                return True, response.json()
        except Exception:
            pass
        time.sleep(2)
    return False, None

def deploy_canary():
    """Deploy canary version"""
    logger.info("Starting Canary Deployment...")
    
    simulation_mode = os.getenv("SIMULATION_MODE", "true").lower() == "true"
    
    if simulation_mode:
        logger.info("Running in simulation mode")
        
        # Simulate deployment steps
        steps = [
            "Applying Helm configuration",
            "Waiting for pods to be ready", 
            "Configuring traffic routing",
            "Starting health checks"
        ]
        
        results = []
        for step in steps:
            logger.info(f"Step: {step}")
            time.sleep(1)  # Simulate work
            results.append({"step": step, "status": "success", "duration": 1.0})
        
        return {
            "status": "success",
            "deployment_id": f"canary_{int(time.time())}",
            "steps": results,
            "simulation_mode": True
        }
    
    else:
        # Production deployment
        results = []
        
        # Step 1: Apply Helm chart
        logger.info("Applying Helm configuration...")
        success, stdout, stderr = run_command(
            "helm upgrade --install atom-canary ./infra/helm/ --set global.environment=canary"
        )
        
        results.append({
            "step": "helm_apply",
            "status": "success" if success else "failed",
            "output": stdout,
            "error": stderr
        })
        
        if not success:
            return {"status": "failed", "error": "Helm deployment failed", "results": results}
        
        # Step 2: Wait for rollout
        logger.info("Waiting for rollout to complete...")
        success, stdout, stderr = run_command(
            "kubectl rollout status deployment/atom-core --timeout=120s"
        )
        
        results.append({
            "step": "rollout_status",
            "status": "success" if success else "failed",
            "output": stdout,
            "error": stderr
        })
        
        if not success:
            return {"status": "failed", "error": "Rollout failed", "results": results}
        
        # Step 3: Health check
        logger.info("Performing health checks...")
        healthy, health_data = check_service_health("http://localhost:10001")
        
        results.append({
            "step": "health_check",
            "status": "success" if healthy else "failed",
            "health_data": health_data
        })
        
        return {
            "status": "success" if healthy else "failed",
            "deployment_id": f"canary_{int(time.time())}",
            "results": results,
            "simulation_mode": False
        }

def main():
    """Main deployment function"""
    try:
        result = deploy_canary()
        
        # Save deployment report
        os.makedirs("reports", exist_ok=True)
        with open("reports/J1_canary_deployment.json", "w") as f:
            json.dump(result, f, indent=2)
        
        if result["status"] == "success":
            logger.info("✅ Canary deployment successful")
            print("Canary deployment completed successfully")
        else:
            logger.error("❌ Canary deployment failed")
            print(f"Canary deployment failed: {result.get('error', 'Unknown error')}")
            
        return result["status"] == "success"
        
    except Exception as e:
        logger.error(f"Deployment error: {e}")
        print(f"Deployment error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)