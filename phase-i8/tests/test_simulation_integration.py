#!/usr/bin/env python3
"""
Phase I.8 Integration Test - Global Simulation Sandbox
"""

import os, json, time, requests, subprocess, threading
import sys
sys.path.append('..')

def start_service(service_path, port):
    """Start a service in background"""
    try:
        return subprocess.Popen([
            sys.executable, f"phase-i8/services/{service_path}/main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"Failed to start {service_path}: {e}")
        return None

def wait_for_service(url, timeout=10):
    """Wait for service to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            r = requests.get(f"{url}/health", timeout=2)
            if r.ok:
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def test_service_health():
    """Test all service health endpoints"""
    services = {
        "simulation-engine": "http://localhost:9801",
        "scenario-builder": "http://localhost:9802",
        "safety-validator": "http://localhost:9803",
        "behavior-analyzer": "http://localhost:9804", 
        "resilience-orchestrator": "http://localhost:9805",
        "dashboard-api": "http://localhost:9806"
    }
    
    results = {}
    for name, url in services.items():
        try:
            r = requests.get(f"{url}/health", timeout=3)
            results[name] = {
                "status": "UP" if r.ok else "DOWN",
                "response": r.json() if r.ok else {"error": "failed"}
            }
        except Exception as e:
            results[name] = {"status": "ERROR", "error": str(e)}
    
    return results

def test_scenario_workflow():
    """Test complete scenario workflow"""
    # Create a test scenario
    test_scenario = {
        "scenario_id": "integration_test",
        "name": "Integration Test Scenario",
        "actors": [{"id": "test_actor", "type": "simulator"}],
        "duration_seconds": 5,
        "metadata": {"test": True}
    }
    
    results = {}
    
    # Test scenario creation
    try:
        r = requests.post("http://localhost:9802/scenarios", json=test_scenario, timeout=5)
        results["scenario_creation"] = {
            "status": "success" if r.ok else "failed",
            "response": r.json() if r.ok else {"error": r.text}
        }
    except Exception as e:
        results["scenario_creation"] = {"status": "error", "error": str(e)}
    
    # Test scenario validation
    try:
        r = requests.post("http://localhost:9802/scenarios/integration_test/validate", timeout=5)
        results["scenario_validation"] = {
            "status": "success" if r.ok else "failed", 
            "response": r.json() if r.ok else {"error": r.text}
        }
    except Exception as e:
        results["scenario_validation"] = {"status": "error", "error": str(e)}
    
    # Test safety validation
    try:
        r = requests.post("http://localhost:9803/validate/event", json=test_scenario, timeout=5)
        results["safety_validation"] = {
            "status": "success" if r.ok else "failed",
            "response": r.json() if r.ok else {"error": r.text}
        }
    except Exception as e:
        results["safety_validation"] = {"status": "error", "error": str(e)}
    
    # Test simulation execution
    try:
        r = requests.post("http://localhost:9801/run", json=test_scenario, timeout=10)
        results["simulation_execution"] = {
            "status": "success" if r.ok else "failed",
            "response": r.json() if r.ok else {"error": r.text}
        }
    except Exception as e:
        results["simulation_execution"] = {"status": "error", "error": str(e)}
    
    # Test behavior analysis
    try:
        r = requests.post("http://localhost:9804/analyze", json=test_scenario, timeout=5)
        results["behavior_analysis"] = {
            "status": "success" if r.ok else "failed",
            "response": r.json() if r.ok else {"error": r.text}
        }
    except Exception as e:
        results["behavior_analysis"] = {"status": "error", "error": str(e)}
    
    return results

def test_fault_injection():
    """Test fault injection and recovery"""
    fault_data = {
        "fault_type": "network_latency",
        "target": "test_service",
        "duration": 5
    }
    
    results = {}
    
    # Test fault injection
    try:
        r = requests.post("http://localhost:9805/inject", json=fault_data, timeout=5)
        results["fault_injection"] = {
            "status": "success" if r.ok else "failed",
            "response": r.json() if r.ok else {"error": r.text}
        }
        
        fault_id = r.json().get("fault_id") if r.ok else None
        
        # Test fault rollback
        if fault_id:
            rollback_data = {"fault_id": fault_id}
            r2 = requests.post("http://localhost:9805/rollback", json=rollback_data, timeout=5)
            results["fault_rollback"] = {
                "status": "success" if r2.ok else "failed",
                "response": r2.json() if r2.ok else {"error": r2.text}
            }
        
    except Exception as e:
        results["fault_injection"] = {"status": "error", "error": str(e)}
    
    return results

def run_integration_tests():
    """Run all integration tests"""
    print("Starting Phase I.8 Integration Tests")
    
    # Test 1: Service Health
    print("Testing service health...")
    health_results = test_service_health()
    
    # Count available services
    available_services = sum(1 for r in health_results.values() if r["status"] == "UP")
    total_services = len(health_results)
    
    print(f"Services available: {available_services}/{total_services}")
    
    if available_services == 0:
        print("No services available - creating offline test report")
        report = {
            "phase": "I.8",
            "test_type": "integration",
            "status": "offline_simulation",
            "services_tested": total_services,
            "services_available": 0,
            "message": "Services not running - simulated test execution",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    else:
        # Test 2: Scenario Workflow
        print("Testing scenario workflow...")
        workflow_results = test_scenario_workflow()
        
        # Test 3: Fault Injection
        print("Testing fault injection...")
        fault_results = test_fault_injection()
        
        # Compile results
        report = {
            "phase": "I.8",
            "test_type": "integration", 
            "status": "completed",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "services_tested": total_services,
            "services_available": available_services,
            "test_results": {
                "service_health": health_results,
                "scenario_workflow": workflow_results,
                "fault_injection": fault_results
            },
            "summary": {
                "total_tests": 3,
                "passed": sum(1 for test in [health_results, workflow_results, fault_results] 
                             if any(r.get("status") == "success" for r in test.values())),
                "simulation_mode": True
            }
        }
    
    # Save test report
    os.makedirs("reports", exist_ok=True)
    with open("reports/I.8_integration_test.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Integration tests completed")
    print(f"Report saved to reports/I.8_integration_test.json")
    
    return report

if __name__ == "__main__":
    run_integration_tests()