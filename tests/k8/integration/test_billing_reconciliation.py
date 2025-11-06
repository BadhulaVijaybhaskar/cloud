import json, os
def test_recon_exists():
    path="reports/k8/billing_reconciliation.json"
    assert os.path.exists(path), "reconciliation report missing"
    data=json.load(open(path))
    assert data["events_count"]>=0