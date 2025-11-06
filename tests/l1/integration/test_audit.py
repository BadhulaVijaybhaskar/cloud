import json, os, requests, time, subprocess

def test_l1_audit_integration():
    # Ensure K.9 telemetry exists
    if not os.path.exists("reports/k9/telemetry.json"):
        subprocess.run(["python", "services/k9-agent-core/telemetry/telemetry_collector.py"])
    
    # Start audit engine
    proc = subprocess.Popen(["python", "services/l1-audit-engine/src/main.py"])
    time.sleep(2)
    
    try:
        # Test audit endpoint
        resp = requests.get("http://localhost:8810/v1/audit")
        assert resp.status_code == 200
        
        audit = resp.json()
        assert "audit_id" in audit
        assert audit["k9_integration"]["telemetry_found"] == True
        assert audit["overall_status"] == "PASS"
        
        # Verify audit report file
        assert os.path.exists("reports/l1/post_integration_audit.json")
        
    finally:
        proc.terminate()

def test_audit_report_structure():
    if os.path.exists("reports/l1/post_integration_audit.json"):
        with open("reports/l1/post_integration_audit.json") as f:
            audit = json.load(f)
        
        assert "k9_integration" in audit
        assert "spend_validation" in audit["k9_integration"]
        assert "compliance_check" in audit["k9_integration"]