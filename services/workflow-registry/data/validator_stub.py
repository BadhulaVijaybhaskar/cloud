"""
Minimal validator stub for WPKs.
This is a starting point. Replace schema validation with a proper JSON Schema or yamale-based check.
"""

import yaml
from datetime import datetime

WPK_SCHEMA_KEYS = ["id", "version", "name", "description", "safety", "nodes"]

def validate_wpk_manifest(yaml_bytes):
    try:
        manifest = yaml.safe_load(yaml_bytes)
    except Exception as e:
        return False, f"YAML parse error: {e}"

    missing = [k for k in WPK_SCHEMA_KEYS if k not in manifest]
    if missing:
        return False, f"Missing required keys: {missing}"

    # Safety.mode default
    safety = manifest.get("safety", {})
    if "mode" not in safety:
        manifest.setdefault("safety", {})["mode"] = "manual"

    # Basic node sanity
    nodes = manifest.get("nodes", [])
    if not isinstance(nodes, list) or len(nodes) == 0:
        return False, "Manifest must contain at least one node in 'nodes' list."

    # Add created_at if missing
    manifest.setdefault("created_at", datetime.utcnow().isoformat() + "Z")
    return True, manifest

# Example usage
if __name__ == "__main__":
    with open("examples/playbooks/restart-unhealthy.wpk.yaml", "r") as f:
        ok, res = validate_wpk_manifest(f.read())
        if not ok:
            print("Validation failed:", res)
        else:
            print("Validation OK. Manifest id:", res.get("id"))
