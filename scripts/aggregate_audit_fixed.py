#!/usr/bin/env python3
"""
Aggregate Phase A Policy Review audit results into consolidated matrix.
Generates JSON, Markdown, and CSV reports from individual audit files.
"""

import os
import json
import csv
from datetime import datetime, timezone
from typing import Dict, List, Any
import glob
import re

class AuditAggregator:
    """Aggregates audit results into policy matrix."""
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = reports_dir
        self.audit_files = self._find_audit_files()
        
    def _find_audit_files(self) -> List[str]:
        """Find all audit report files."""
        pattern = os.path.join(self.reports_dir, "Audit_*.md")
        return glob.glob(pattern)
    
    def aggregate_results(self) -> Dict[str, Any]:
        """Aggregate all audit results into policy matrix."""
        
        matrix = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "phase": "Phase A Policy Review",
                "version": "1.0.0",
                "total_policies": 0,
                "summary": {}
            },
            "policies": []
        }
        
        # Define policy mappings
        policy_mappings = {
            "Audit_Cosign_Vault.md": {
                "category": "Security & Secrets",
                "policies": [
                    {
                        "name": "Cosign Signature Enforcement",
                        "description": "All WPK packages must be signed with cosign",
                        "implementation_file": "services/workflow-registry/cosign_enforcer.py"
                    },
                    {
                        "name": "Vault Secret Management", 
                        "description": "Secrets retrieved securely via HashiCorp Vault",
                        "implementation_file": "services/workflow-registry/vault_client.py"
                    }
                ]
            },
            "Audit_Dryrun.md": {
                "category": "Policy Engine",
                "policies": [
                    {
                        "name": "Static Security Validation",
                        "description": "WPK packages validated for security issues before execution",
                        "implementation_file": "services/workflow-registry/validator/static_validator.py"
                    },
                    {
                        "name": "Policy Engine Risk Assessment",
                        "description": "Risk-based approval workflow for WPK execution",
                        "implementation_file": "services/workflow-registry/validator/policy_engine.py"
                    }
                ]
            },
            "Audit_RLS.md": {
                "category": "Tenancy & Access Control",
                "policies": [
                    {
                        "name": "Row Level Security (RLS)",
                        "description": "Database-level tenant isolation using RLS policies",
                        "implementation_file": "infra/sql/rls_policies.sql"
                    },
                    {
                        "name": "Cross-Tenant Access Prevention",
                        "description": "Prevent unauthorized cross-tenant data access",
                        "implementation_file": "scripts/test_tenancy.py"
                    }
                ]
            },
            "Audit_Backup_DR.md": {
                "category": "Backup & Disaster Recovery",
                "policies": [
                    {
                        "name": "Automated Backup Process",
                        "description": "Regular automated backups of workflow execution data",
                        "implementation_file": "infra/backup/backup_workflow_runs.sh"
                    },
                    {
                        "name": "Backup Integrity Verification",
                        "description": "SHA-256 verification of backup file integrity",
                        "implementation_file": "infra/scripts/restore_from_backup.sh"
                    }
                ]
            },
            "Audit_Observability.md": {
                "category": "Monitoring & Alerting",
                "policies": [
                    {
                        "name": "Workflow Failure Monitoring",
                        "description": "Prometheus alerts for workflow execution failures",
                        "implementation_file": "infra/monitoring/prometheus/alerts-workflow.yaml"
                    },
                    {
                        "name": "Security Event Alerting",
                        "description": "Critical alerts for unsigned uploads and anomalies",
                        "implementation_file": "infra/monitoring/prometheus/alerts-workflow.yaml"
                    }
                ]
            },
            "Audit_Logs_ETL.md": {
                "category": "Audit & Compliance",
                "policies": [
                    {
                        "name": "Immutable Audit Logging",
                        "description": "SHA-256 verified audit logs for all operations",
                        "implementation_file": "infra/audit/s3_audit_logger.py"
                    },
                    {
                        "name": "ETL Data Export",
                        "description": "Structured export of workflow data for analysis",
                        "implementation_file": "services/etl/export_runs/export_to_jsonl.py"
                    }
                ]
            }
        }
        
        # Process each audit file
        for audit_file in self.audit_files:
            filename = os.path.basename(audit_file)
            
            if filename in policy_mappings:
                file_status = self._parse_audit_file(audit_file)
                mapping = policy_mappings[filename]
                
                for policy_def in mapping["policies"]:
                    policy = {
                        "name": policy_def["name"],
                        "category": mapping["category"],
                        "description": policy_def["description"],
                        "implementation_file": policy_def["implementation_file"],
                        "implemented": True,  # All policies have implementations
                        "enforced": file_status["enforced"],
                        "status": file_status["status"],
                        "evidence_file": audit_file,
                        "notes": file_status["notes"],
                        "missing_dependencies": file_status.get("missing_dependencies", [])
                    }
                    
                    matrix["policies"].append(policy)
        
        # Generate summary
        matrix["metadata"]["total_policies"] = len(matrix["policies"])
        matrix["metadata"]["summary"] = self._generate_summary(matrix["policies"])
        
        return matrix
    
    def _parse_audit_file(self, audit_file: str) -> Dict[str, Any]:
        """Parse individual audit file for status and notes."""
        
        try:
            with open(audit_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine overall status
            if "BLOCKED" in content:
                status = "BLOCKED"
                enforced = False
            elif "PASS" in content and "FAIL" not in content:
                status = "PASS"
                enforced = True
            elif "FAIL" in content:
                status = "FAIL"
                enforced = False
            else:
                status = "UNKNOWN"
                enforced = False
            
            # Extract notes and dependencies
            notes = []
            missing_deps = []
            
            # Look for missing dependencies
            if "Missing Dependencies:" in content or "Missing environment variables:" in content:
                dep_section = re.search(r'Missing [Dd]ependencies?:.*?(?=\n\n|\n#|\Z)', content, re.DOTALL)
                if dep_section:
                    dep_text = dep_section.group(0)
                    # Extract dependency items
                    deps = re.findall(r'[-*]\s*([^\n]+)', dep_text)
                    missing_deps.extend(deps)
            
            # Extract key notes
            if "BLOCKED" in content:
                notes.append("Missing external dependencies")
            if "simulation" in content.lower():
                notes.append("Tested in simulation mode")
            if "ready" in content.lower():
                notes.append("Implementation ready for deployment")
            
            return {
                "status": status,
                "enforced": enforced,
                "notes": "; ".join(notes) if notes else "See audit file for details",
                "missing_dependencies": missing_deps
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "enforced": False,
                "notes": f"Failed to parse audit file: {e}",
                "missing_dependencies": []
            }
    
    def _generate_summary(self, policies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics."""
        
        total = len(policies)
        passed = sum(1 for p in policies if p["status"] == "PASS")
        failed = sum(1 for p in policies if p["status"] == "FAIL")
        blocked = sum(1 for p in policies if p["status"] == "BLOCKED")
        
        # Category breakdown
        categories = {}
        for policy in policies:
            cat = policy["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "pass": 0, "fail": 0, "blocked": 0}
            
            categories[cat]["total"] += 1
            if policy["status"] == "PASS":
                categories[cat]["pass"] += 1
            elif policy["status"] == "FAIL":
                categories[cat]["fail"] += 1
            elif policy["status"] == "BLOCKED":
                categories[cat]["blocked"] += 1
        
        return {
            "total_policies": total,
            "passed": passed,
            "failed": failed,
            "blocked": blocked,
            "pass_rate": round(passed / total * 100, 1) if total > 0 else 0,
            "categories": categories
        }
    
    def generate_markdown_report(self, matrix: Dict[str, Any]) -> str:
        """Generate markdown policy matrix report."""
        
        md = []
        md.append("# Phase A Policy Matrix")
        md.append("")
        md.append(f"**Generated:** {matrix['metadata']['generated_at']}")
        md.append(f"**Phase:** {matrix['metadata']['phase']}")
        md.append(f"**Total Policies:** {matrix['metadata']['total_policies']}")
        md.append("")
        
        # Summary
        summary = matrix['metadata']['summary']
        md.append("## Summary")
        md.append("")
        md.append(f"- **PASS:** {summary['passed']} policies")
        md.append(f"- **FAIL:** {summary['failed']} policies") 
        md.append(f"- **BLOCKED:** {summary['blocked']} policies")
        md.append(f"- **Pass Rate:** {summary['pass_rate']}%")
        md.append("")
        
        # Category breakdown
        md.append("## Category Breakdown")
        md.append("")
        for category, stats in summary['categories'].items():
            md.append(f"### {category}")
            md.append(f"- Total: {stats['total']}")
            md.append(f"- Pass: {stats['pass']}")
            md.append(f"- Fail: {stats['fail']}")
            md.append(f"- Blocked: {stats['blocked']}")
            md.append("")
        
        # Policy details table
        md.append("## Policy Details")
        md.append("")
        md.append("| Policy | Category | Implemented | Enforced | Status | Notes |")
        md.append("|--------|----------|-------------|----------|--------|-------|")
        
        for policy in matrix['policies']:
            status_text = {
                "PASS": "PASS",
                "FAIL": "FAIL", 
                "BLOCKED": "BLOCKED"
            }.get(policy['status'], "UNKNOWN")
            
            implemented = "Yes" if policy['implemented'] else "No"
            enforced = "Yes" if policy['enforced'] else "No"
            
            md.append(f"| {policy['name']} | {policy['category']} | {implemented} | {enforced} | {status_text} | {policy['notes']} |")
        
        md.append("")
        
        # Missing dependencies
        all_deps = set()
        for policy in matrix['policies']:
            all_deps.update(policy.get('missing_dependencies', []))
        
        if all_deps:
            md.append("## Missing Dependencies")
            md.append("")
            for dep in sorted(all_deps):
                md.append(f"- {dep}")
            md.append("")
        
        return "\n".join(md)
    
    def generate_csv_report(self, matrix: Dict[str, Any]) -> List[List[str]]:
        """Generate CSV policy matrix report."""
        
        output = []
        
        # Header
        header = [
            "Policy Name",
            "Category", 
            "Description",
            "Implementation File",
            "Implemented",
            "Enforced",
            "Status",
            "Evidence File",
            "Notes",
            "Missing Dependencies"
        ]
        output.append(header)
        
        # Policy rows
        for policy in matrix['policies']:
            row = [
                policy['name'],
                policy['category'],
                policy['description'],
                policy['implementation_file'],
                "Yes" if policy['implemented'] else "No",
                "Yes" if policy['enforced'] else "No",
                policy['status'],
                policy['evidence_file'],
                policy['notes'],
                "; ".join(policy.get('missing_dependencies', []))
            ]
            output.append(row)
        
        return output

def main():
    """Generate Phase A Policy Matrix reports."""
    
    aggregator = AuditAggregator()
    matrix = aggregator.aggregate_results()
    
    # Generate JSON report
    json_file = "reports/PhaseA_PolicyMatrix.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(matrix, f, indent=2)
    print(f"Generated: {json_file}")
    
    # Generate Markdown report
    md_content = aggregator.generate_markdown_report(matrix)
    md_file = "reports/PhaseA_PolicyMatrix.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Generated: {md_file}")
    
    # Generate CSV report
    csv_data = aggregator.generate_csv_report(matrix)
    csv_file = "reports/PhaseA_PolicyMatrix.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
    print(f"Generated: {csv_file}")
    
    # Print summary
    summary = matrix['metadata']['summary']
    print(f"\nPhase A Policy Review Summary:")
    print(f"  PASS: {summary['passed']}")
    print(f"  FAIL: {summary['failed']}")
    print(f"  BLOCKED: {summary['blocked']}")
    print(f"  Total: {summary['total_policies']}")

if __name__ == "__main__":
    main()