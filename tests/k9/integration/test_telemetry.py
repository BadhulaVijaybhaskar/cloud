import json, os

def test_telemetry_file_exists():
    path = "reports/k9/telemetry.json"
    assert os.path.exists(path), "telemetry.json missing"
    data = json.load(open(path))
    assert "metrics" in data
    assert "ad_spend_usd" in data["metrics"]