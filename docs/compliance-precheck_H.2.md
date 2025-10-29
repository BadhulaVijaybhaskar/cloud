# Compliance Precheck — Phase H.2 Neural Fabric Scheduler Readiness

Purpose: quick agent-run preflight. Write `/reports/H.2_precheck.json` and logs to `/reports/logs/H.2_precheck.log`.

Checks (agent must run and capture output):

1) Env summary
```bash
mkdir -p reports/logs
( echo "ENV SUMMARY"; env | grep -E 'POSTGRES_DSN|VAULT_ADDR|COSIGN_KEY_PATH|PQC_MODE|NEURAL_FABRIC_MODE|GPU_NODES|MODEL_STORE_URL|SIMULATION_MODE' ) > /reports/logs/H.2_precheck_env.txt 2>&1 || true
```

2. Postgres reachable (quick)

```bash
python - <<'PY' > /reports/logs/H.2_precheck_postgres.log 2>&1
import os,json,psycopg2
dsn=os.getenv("POSTGRES_DSN")
out={"postgres":"MISSING" if not dsn else "UNKNOWN"}
if dsn:
  try:
    psycopg2.connect(dsn,connect_timeout=3).close(); out["postgres"]="REACHABLE"
  except Exception as e:
    out["postgres"]="ERROR:"+str(e)
print(json.dumps(out))
PY
```

3. Vault & Cosign presence

```bash
python - <<'PY' > /reports/logs/H.2_precheck_vault.log 2>&1
import os,json
out={"vault":"UP" if os.getenv("VAULT_ADDR") else "MISSING","cosign":"OK" if os.getenv("COSIGN_KEY_PATH") and os.path.exists(os.getenv("COSIGN_KEY_PATH")) else "MISSING"}
print(json.dumps(out))
PY
```

4. GPU nodes connect check (best-effort)

```bash
python - <<'PY' > /reports/logs/H.2_precheck_gpu.log 2>&1
import os,json
nodes=os.getenv("GPU_NODES","")
out={"gpu_nodes":nodes or "NONE"}
print(json.dumps(out))
PY
```

5. Decision logic -> write `/reports/H.2_precheck.json`
   Rules:

* If POSTGRES reachable and VAULT present and (GPU_NODES set or SIMULATION_MODE=true) => PROCEED
* If registry missing but SIMULATION_MODE true => PROCEED_SIMULATION
* Else => BLOCK

Agent must implement above logic and save JSON.

End of precheck.