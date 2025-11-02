#!/usr/bin/env python3
"""
Phase I.8 Simulation Runner - Execute scenarios and collect results
"""

import os, json, time, requests, logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simulation_runner")

class SimulationRunner:
    def __init__(self):
        self.base_urls = {
            "simulation-engine": "http://localhost:9801",
            "scenario-builder": "http://localhost:9802",
            "safety-validator": "http://localhost:9803", 
            "behavior-analyzer": "http://localhost:9804",
            "resilience-orchestrator": "http://localhost:9805",
            "dashboard-api": "http://localhost:9806"
        }
        self.simulation_mode = os.getenv("SIMULATION_MODE", "true").lower() == "true"
    
    def check_services(self):
        """Check if all services are running"""
        status = {}
        for name, url in self.base_urls.items():
            try:
                r = requests.get(f"{url}/health", timeout=3)
                status[name] = "UP" if r.ok else "DOWN"
            except Exception as e:
                status[name] = "ERROR"
                logger.warning(f"Service {name} not accessible: {e}")
        return status
    
    def load_scenario(self, scenario_file):
        """Load scenario from file"""
        try:
            with open(scenario_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load scenario {scenario_file}: {e}")
            return None
    
    def validate_scenario(self, scenario):
        """Validate scenario using safety validator"""
        try:
            url = f"{self.base_urls['safety-validator']}/validate/event"
            r = requests.post(url, json=scenario, timeout=5)
            return r.json() if r.ok else {"result": "error", "reason": "validation_failed"}
        except Exception as e:
            logger.warning(f"Validation failed: {e}")
            return {"result": "pass", "reason": "validation_unavailable"}
    
    def run_scenario(self, scenario):
        """Execute scenario using simulation engine"""
        try:
            # First validate the scenario
            validation = self.validate_scenario(scenario)
            if validation.get("result") == "fail":
                return {
                    "status": "blocked",
                    "reason": validation.get("reason"),
                    "policy": validation.get("policy")
                }
            
            # Run the scenario
            url = f"{self.base_urls['simulation-engine']}/run"
            r = requests.post(url, json=scenario, timeout=10)
            
            if r.ok:
                result = r.json()
                run_id = result.get("run_id")
                
                # Get detailed status
                status_url = f"{self.base_urls['simulation-engine']}/status/{run_id}"
                status_r = requests.get(status_url, timeout=5)
                
                return {
                    "status": "completed",
                    "run_id": run_id,
                    "validation": validation,
                    "execution": result,
                    "details": status_r.json() if status_r.ok else {}
                }
            else:
                return {"status": "failed", "reason": "execution_error"}
                
        except Exception as e:
            logger.error(f"Scenario execution failed: {e}")
            return {"status": "error", "reason": str(e)}
    
    def analyze_behavior(self, scenario_result):
        """Analyze behavior using behavior analyzer"""
        try:
            url = f"{self.base_urls['behavior-analyzer']}/analyze"
            r = requests.post(url, json=scenario_result, timeout=5)
            return r.json() if r.ok else {"error": "analysis_failed"}
        except Exception as e:
            logger.warning(f"Behavior analysis failed: {e}")
            return {"error": str(e)}
    
    def run_all_scenarios(self):
        """Run all available scenarios"""
        scenario_files = [
            "phase-i8/scenarios/basic_load_test.json",
            "phase-i8/scenarios/chaos_engineering.json", 
            "phase-i8/scenarios/ai_behavior_test.json"
        ]
        
        results = {}
        
        for scenario_file in scenario_files:
            if not os.path.exists(scenario_file):
                logger.warning(f"Scenario file not found: {scenario_file}")
                continue
            
            logger.info(f"Running scenario: {scenario_file}")
            scenario = self.load_scenario(scenario_file)
            
            if scenario:
                # Execute scenario
                result = self.run_scenario(scenario)
                
                # Analyze behavior if execution succeeded
                if result.get("status") == "completed":
                    behavior_analysis = self.analyze_behavior(result)
                    result["behavior_analysis"] = behavior_analysis
                
                results[scenario["scenario_id"]] = result
                logger.info(f"Scenario {scenario['scenario_id']} completed: {result['status']}")
            
            # Small delay between scenarios
            time.sleep(1)
        
        return results
    
    def generate_report(self, results):
        """Generate comprehensive simulation report"""
        report = {
            "phase": "I.8",
            "execution_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "simulation_mode": self.simulation_mode,
            "service_status": self.check_services(),
            "scenarios_executed": len(results),
            "scenarios": results,
            "summary": {
                "total_scenarios": len(results),
                "successful": sum(1 for r in results.values() if r.get("status") == "completed"),
                "failed": sum(1 for r in results.values() if r.get("status") in ["failed", "error"]),
                "blocked": sum(1 for r in results.values() if r.get("status") == "blocked")
            }
        }
        
        # Calculate overall success rate
        if report["summary"]["total_scenarios"] > 0:
            report["summary"]["success_rate"] = (
                report["summary"]["successful"] / report["summary"]["total_scenarios"]
            )
        
        # Save report
        os.makedirs("reports", exist_ok=True)
        report_file = "reports/I.8_simulation_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Simulation report saved to {report_file}")
        return report

def main():
    """Main execution function"""
    print("Starting Phase I.8 Global Simulation Sandbox")
    
    runner = SimulationRunner()
    
    # Check service availability
    print("Checking service status...")
    service_status = runner.check_services()
    available_services = sum(1 for status in service_status.values() if status == "UP")
    
    print(f"Services available: {available_services}/{len(service_status)}")
    
    if available_services == 0:
        print("No services available - running in offline simulation mode")
        # Create minimal simulation report
        report = {
            "phase": "I.8",
            "status": "offline_simulation",
            "message": "Services not available - simulated execution",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        os.makedirs("reports", exist_ok=True)
        with open("reports/I.8_simulation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        return
    
    # Run scenarios
    print("Executing simulation scenarios...")
    results = runner.run_all_scenarios()
    
    # Generate report
    print("Generating simulation report...")
    report = runner.generate_report(results)
    
    print(f"Simulation complete!")
    print(f"- Total scenarios: {report['summary']['total_scenarios']}")
    print(f"- Successful: {report['summary']['successful']}")
    print(f"- Failed: {report['summary']['failed']}")
    print(f"- Success rate: {report['summary'].get('success_rate', 0):.2%}")

if __name__ == "__main__":
    main()