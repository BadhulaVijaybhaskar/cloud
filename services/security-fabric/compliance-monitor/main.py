from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List

app = FastAPI(title="ATOM Compliance Monitor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

# P-Policy compliance framework
P_POLICIES = {
    "P1": {
        "name": "Data Privacy",
        "description": "PII protection and data minimization",
        "checks": [
            "encryption_at_rest",
            "encryption_in_transit",
            "data_anonymization",
            "consent_management",
            "right_to_deletion"
        ]
    },
    "P2": {
        "name": "Secrets & Signing",
        "description": "Key management and artifact signing",
        "checks": [
            "secret_rotation",
            "cosign_verification",
            "key_escrow",
            "certificate_validation",
            "secure_key_storage"
        ]
    },
    "P3": {
        "name": "Execution Safety",
        "description": "Runtime security and sandboxing",
        "checks": [
            "container_scanning",
            "runtime_protection",
            "privilege_escalation_prevention",
            "network_segmentation",
            "resource_limits"
        ]
    },
    "P4": {
        "name": "Observability",
        "description": "Monitoring and audit trails",
        "checks": [
            "audit_logging",
            "metrics_collection",
            "alerting_system",
            "log_retention",
            "incident_response"
        ]
    },
    "P5": {
        "name": "Multi-Tenancy",
        "description": "Tenant isolation and access control",
        "checks": [
            "tenant_isolation",
            "rbac_enforcement",
            "data_segregation",
            "cross_tenant_prevention",
            "identity_verification"
        ]
    },
    "P6": {
        "name": "Performance Budget",
        "description": "Resource usage and SLA compliance",
        "checks": [
            "resource_quotas",
            "performance_monitoring",
            "sla_compliance",
            "capacity_planning",
            "auto_scaling"
        ]
    }
}

scan_count = 0
last_scan_results = {}

def simulate_policy_check(policy_id: str, check_name: str) -> Dict[str, Any]:
    """Simulate compliance check results"""
    import random
    
    # Simulate different compliance levels
    base_score = random.uniform(0.7, 1.0)
    
    # Some checks are more likely to pass than others
    if check_name in ["audit_logging", "metrics_collection", "encryption_in_transit"]:
        base_score = random.uniform(0.9, 1.0)
    elif check_name in ["cosign_verification", "container_scanning"]:
        base_score = random.uniform(0.6, 0.9)
    
    passed = base_score >= 0.8
    
    return {
        "check": check_name,
        "passed": passed,
        "score": round(base_score * 100, 1),
        "details": f"Simulated check for {check_name}",
        "remediation": f"Improve {check_name} implementation" if not passed else None,
        "timestamp": datetime.utcnow().isoformat()
    }

def audit_log(action: str, details: Dict[str, Any]):
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "service": "compliance-monitor",
        "action": action,
        "details": details,
        "sha256": hashlib.sha256(json.dumps(details, sort_keys=True).encode()).hexdigest()
    }
    
    os.makedirs("reports/logs", exist_ok=True)
    with open("reports/logs/compliance_audit.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "compliance-monitor",
        "env": "SIM" if SIMULATION_MODE else "LIVE",
        "policies_monitored": len(P_POLICIES),
        "scans_performed": scan_count,
        "last_scan": last_scan_results.get("timestamp") if last_scan_results else None,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/scan")
async def run_compliance_scan():
    global scan_count, last_scan_results
    scan_count += 1
    
    scan_id = f"scan-{int(datetime.utcnow().timestamp())}"
    scan_results = {
        "scan_id": scan_id,
        "timestamp": datetime.utcnow().isoformat(),
        "policies": {},
        "summary": {
            "total_policies": len(P_POLICIES),
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "overall_score": 0
        }
    }
    
    total_checks = 0
    passed_checks = 0
    
    # Run compliance checks for each P-Policy
    for policy_id, policy_info in P_POLICIES.items():
        policy_results = {
            "name": policy_info["name"],
            "description": policy_info["description"],
            "checks": [],
            "passed": 0,
            "total": len(policy_info["checks"]),
            "score": 0
        }
        
        # Run each check for this policy
        for check_name in policy_info["checks"]:
            check_result = simulate_policy_check(policy_id, check_name)
            policy_results["checks"].append(check_result)
            
            if check_result["passed"]:
                policy_results["passed"] += 1
                passed_checks += 1
            
            total_checks += 1
        
        # Calculate policy score
        policy_results["score"] = round((policy_results["passed"] / policy_results["total"]) * 100, 1)
        scan_results["policies"][policy_id] = policy_results
    
    # Calculate overall summary
    scan_results["summary"]["total_checks"] = total_checks
    scan_results["summary"]["passed_checks"] = passed_checks
    scan_results["summary"]["failed_checks"] = total_checks - passed_checks
    scan_results["summary"]["overall_score"] = round((passed_checks / total_checks) * 100, 1) if total_checks > 0 else 0
    
    # Store results
    last_scan_results = scan_results
    
    # Log the scan
    audit_log("compliance_scan", {
        "scan_id": scan_id,
        "overall_score": scan_results["summary"]["overall_score"],
        "passed_checks": passed_checks,
        "total_checks": total_checks
    })
    
    return scan_results

@app.get("/report")
async def generate_compliance_report():
    if not last_scan_results:
        raise HTTPException(status_code=404, detail="No scan results available. Run /scan first.")
    
    # Generate markdown report
    report_lines = [
        "# ATOM Cloud Compliance Report",
        f"**Generated:** {datetime.utcnow().isoformat()}",
        f"**Scan ID:** {last_scan_results['scan_id']}",
        f"**Overall Score:** {last_scan_results['summary']['overall_score']}%",
        "",
        "## Executive Summary",
        f"- Total Policies: {last_scan_results['summary']['total_policies']}",
        f"- Total Checks: {last_scan_results['summary']['total_checks']}",
        f"- Passed: {last_scan_results['summary']['passed_checks']}",
        f"- Failed: {last_scan_results['summary']['failed_checks']}",
        "",
        "## Policy Compliance Matrix",
        ""
    ]
    
    # Add policy details
    for policy_id, policy_data in last_scan_results["policies"].items():
        status_icon = "✅" if policy_data["score"] >= 95 else "⚠️" if policy_data["score"] >= 80 else "❌"
        report_lines.append(f"{policy_id} {policy_data['name']}: {status_icon} {policy_data['score']}%")
    
    report_lines.extend([
        "",
        "## Detailed Results",
        ""
    ])
    
    # Add detailed check results
    for policy_id, policy_data in last_scan_results["policies"].items():
        report_lines.extend([
            f"### {policy_id}: {policy_data['name']}",
            f"**Description:** {policy_data['description']}",
            f"**Score:** {policy_data['score']}% ({policy_data['passed']}/{policy_data['total']} checks passed)",
            ""
        ])
        
        for check in policy_data["checks"]:
            status = "✅ PASS" if check["passed"] else "❌ FAIL"
            report_lines.append(f"- {check['check']}: {status} ({check['score']}%)")
            if check.get("remediation"):
                report_lines.append(f"  - *Remediation: {check['remediation']}*")
        
        report_lines.append("")
    
    report_lines.extend([
        "## Recommendations",
        "",
        "1. Address all failed checks with score < 80%",
        "2. Implement automated remediation for common issues",
        "3. Schedule regular compliance scans",
        "4. Review and update policies quarterly",
        "",
        "---",
        "*Report generated by ATOM Compliance Monitor*"
    ])
    
    markdown_report = "\n".join(report_lines)
    
    # Save report to file
    os.makedirs("reports", exist_ok=True)
    report_filename = f"reports/compliance_report_{last_scan_results['scan_id']}.md"
    with open(report_filename, "w") as f:
        f.write(markdown_report)
    
    audit_log("generate_report", {
        "scan_id": last_scan_results['scan_id'],
        "report_file": report_filename,
        "overall_score": last_scan_results['summary']['overall_score']
    })
    
    return {
        "report": markdown_report,
        "report_file": report_filename,
        "scan_id": last_scan_results['scan_id'],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/policies")
async def get_policies():
    return {
        "policies": P_POLICIES,
        "count": len(P_POLICIES),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
async def metrics():
    overall_score = last_scan_results.get("summary", {}).get("overall_score", 0) if last_scan_results else 0
    
    return f"""# HELP compliance_monitor_scans_total Total number of compliance scans
# TYPE compliance_monitor_scans_total counter
compliance_monitor_scans_total {scan_count}

# HELP compliance_monitor_overall_score Overall compliance score percentage
# TYPE compliance_monitor_overall_score gauge
compliance_monitor_overall_score {overall_score}

# HELP compliance_monitor_policies_total Number of policies monitored
# TYPE compliance_monitor_policies_total gauge
compliance_monitor_policies_total {len(P_POLICIES)}

# HELP compliance_monitor_last_scan_timestamp Timestamp of last scan
# TYPE compliance_monitor_last_scan_timestamp gauge
compliance_monitor_last_scan_timestamp {int(datetime.utcnow().timestamp()) if last_scan_results else 0}
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8105)