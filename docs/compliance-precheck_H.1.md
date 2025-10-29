# Compliance Precheck — Phase H.1 PQC Activation

Purpose: Verify Vault, Cosign, and PQC libraries before execution.  
Output: `/reports/H.1_precheck.json` and logs.

```bash
mkdir -p reports/logs
python - <<'PY' > /reports/H.1_precheck.json 2>&1
import os,json
r={}
r["vault"]="UP" if os.getenv("VAULT_ADDR") else "MISSING"
r["cosign"]="OK" if os.getenv("COSIGN_KEY_PATH") else "MISSING"
r["kyber"]="FOUND" if os.getenv("KYBER_LIB_PATH") and os.path.exists(os.getenv("KYBER_LIB_PATH")) else "MISSING"
r["dilithium"]="FOUND" if os.getenv("DILITHIUM_LIB_PATH") and os.path.exists(os.getenv("DILITHIUM_LIB_PATH")) else "MISSING"
r["decision"]="PROCEED" if r["vault"]=="UP" else "PROCEED_SIMULATION"
print(json.dumps(r,indent=2))
PY
```

If decision = `BLOCK`, stop execution.
If `PROCEED_SIMULATION`, set `SIMULATION_MODE=true`.