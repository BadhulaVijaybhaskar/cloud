#!/usr/bin/env python3
"""
Phase J.1 Precheck Script - Production Launch Readiness
"""

import os, json, time

def check_environment():
    """Check required environment variables for production deployment"""
    required_vars = [
        "CLOUD_PROVIDER", "REGION", "K8S_CONTEXT", 
        "VAULT_ADDR", "PROM_URL", "GRAFANA_URL", "BILLING_KEY"
    ]
    
    env_status = {}
    missing = False
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            env_status[var] = "SET"
            print(f"✅ {var}={value}")
        else:
            env_status[var] = "MISSING"
            print(f"❌ Missing {var}")
            missing = True
    
    # Determine decision
    if missing:
        decision = "BLOCK"
        print("Precheck failed. Missing environment variables.")
    else:
        decision = "PROCEED"
        print("Precheck success. All required variables set.")
    
    return {
        "decision": decision,
        "missing_env": missing,
        "environment": env_status,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

def check_infrastructure():
    """Check infrastructure readiness"""
    infra_checks = {
        "terraform_available": check_terraform(),
        "kubectl_available": check_kubectl(),
        "helm_available": check_helm()
    }
    
    return infra_checks

def check_terraform():
    """Check if Terraform is available"""
    try:
        import subprocess
        result = subprocess.run(["terraform", "--version"], 
                              capture_output=True, text=True, timeout=5)
        return "available" if result.returncode == 0 else "not_found"
    except Exception:
        return "not_found"

def check_kubectl():
    """Check if kubectl is available"""
    try:
        import subprocess
        result = subprocess.run(["kubectl", "version", "--client"], 
                              capture_output=True, text=True, timeout=5)
        return "available" if result.returncode == 0 else "not_found"
    except Exception:
        return "not_found"

def check_helm():
    """Check if Helm is available"""
    try:
        import subprocess
        result = subprocess.run(["helm", "version"], 
                              capture_output=True, text=True, timeout=5)
        return "available" if result.returncode == 0 else "not_found"
    except Exception:
        return "not_found"

def main():
    """Run Phase J.1 precheck"""
    print("Phase J.1 precheck starting...")
    
    # Create reports directory
    os.makedirs("reports/logs", exist_ok=True)
    
    # Check environment
    env_check = check_environment()
    
    # Check infrastructure tools
    infra_check = check_infrastructure()
    
    # Generate precheck report
    report = {
        "phase": "J.1",
        "precheck_status": "PASS" if env_check["decision"] == "PROCEED" else "FAIL",
        "environment_check": env_check,
        "infrastructure_check": infra_check,
        "recommendations": []
    }
    
    if env_check["decision"] == "BLOCK":
        report["recommendations"].append("Set missing environment variables before proceeding")
    
    if infra_check["terraform_available"] == "not_found":
        report["recommendations"].append("Install Terraform for infrastructure provisioning")
    
    if infra_check["kubectl_available"] == "not_found":
        report["recommendations"].append("Install kubectl for Kubernetes management")
    
    if infra_check["helm_available"] == "not_found":
        report["recommendations"].append("Install Helm for application deployment")
    
    # Save reports
    with open("reports/J1_precheck.json", "w") as f:
        json.dump(report, f, indent=2)
    
    with open("reports/logs/J1_precheck.log", "w") as f:
        f.write(f"Phase J.1 Precheck - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Decision: {env_check['decision']}\n")
        f.write(f"Environment Status: {env_check['environment']}\n")
        f.write(f"Infrastructure Status: {infra_check}\n")
    
    print(f"Precheck complete: {env_check['decision']}")
    print(f"Report saved to reports/J1_precheck.json")
    
    return report

if __name__ == "__main__":
    main()