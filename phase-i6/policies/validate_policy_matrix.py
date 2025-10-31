#!/usr/bin/env python3
# Simple validator: checks required top-level keys and basic rule shapes

import yaml, sys, os, json

PATH = "phase-i6/policies/policy-matrix.yaml"

def load():
    with open(PATH) as f:
        return yaml.safe_load(f)

def check(data):
    ok = True
    if "policies" not in data:
        print("ERROR: 'policies' section missing")
        return False
    for pid, p in data["policies"].items():
        for k in ("id","title","description","enforcement_points","enforcement_mode","rules"):
            if k not in p:
                print(f"ERROR: policy {pid} missing key: {k}")
                ok = False
        if not isinstance(p.get("rules",[]), list):
            print(f"ERROR: policy {pid} rules must be a list")
            ok = False
    return ok

if __name__ == "__main__":
    if not os.path.exists(PATH):
        print("ERROR: policy-matrix.yaml not found at", PATH); sys.exit(2)
    data = load()
    ok = check(data)
    print("VALIDATION:", "PASS" if ok else "FAIL")
    if not ok:
        sys.exit(1)
    else:
        # create a small JSON copy for programmatic use
        out_path = "phase-i6/policies/policy-matrix.json"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path,"w") as fw:
            json.dump(data, fw, indent=2)
        print("Wrote", out_path)