# Compliance Precheck — Phase G.2 Cross-Cloud Replication Readiness

Purpose: quick agent-run preflight. Write output JSON to `/reports/G.2_precheck.json`
and stdout/stderr to `/reports/logs/G.2_precheck.log`.

Run the checks below. Agent must stop with decision BLOCK if registry missing.

---

## Run (agent must execute the shell/python blocks and capture output)

1) Basic env summary (shell)
```bash
mkdir -p reports/logs
( echo "ENV SUMMARY"; env | grep -E 'POSTGRES_DSN|POSTGRES_DSN_PRIMARY|POSTGRES_DSN_SECONDARY|S3_PRIMARY_ENDPOINT|S3_SECONDARY_ENDPOINT|CLOUD_PROVIDER_PRIMARY|CLOUD_PROVIDER_SECONDARY|VAULT_ADDR|COSIGN_KEY_PATH|FEDERATION_TOKEN|SIMULATION_MODE' ) > /reports/logs/G.2_precheck_env.txt 2>&1 || true
```

2. Registry reachable check (HTTP simple)

```bash
python - <<'PY' > /reports/logs/G.2_precheck_registry.log 2>&1
import os,sys,json,requests
out={}
url=os.getenv("GLOBAL_REGISTRY_URL","http://localhost:8401")
try:
  r=requests.get(f"{url}/health", timeout=3)
  out["registry"]="UP" if r.ok else f"DOWN:{r.status_code}"
except Exception as e:
  out["registry"]=f"ERROR:{str(e)}"
print(json.dumps(out))
PY
```

3. Postgres primary/secondary connectivity

```bash
python - <<'PY' > /reports/logs/G.2_precheck_postgres.log 2>&1
import os,json,psycopg2
def check(dsn):
    if not dsn:
        return "MISSING"
    try:
        psycopg2.connect(dsn, connect_timeout=3).close()
        return "REACHABLE"
    except Exception as e:
        return f"ERROR:{str(e)}"
out={}
out["primary"]=check(os.getenv("POSTGRES_DSN_PRIMARY"))
out["secondary"]=check(os.getenv("POSTGRES_DSN_SECONDARY"))
print(json.dumps(out))
PY
```

4. Vault & Cosign presence

```bash
python - <<'PY' > /reports/logs/G.2_precheck_vault_cosign.log 2>&1
import os,json
out={}
out["vault"]="UP" if os.getenv("VAULT_ADDR") else "MISSING"
out["cosign"]="OK" if os.getenv("COSIGN_KEY_PATH") and os.path.exists(os.getenv("COSIGN_KEY_PATH")) else "MISSING"
print(json.dumps(out))
PY
```

5. Cloud provider endpoints (simple TCP/connect check)

```bash
python - <<'PY' > /reports/logs/G.2_precheck_cloud.log 2>&1
import os,socket,json
def can_connect(hostport):
    if not hostport: return "MISSING"
    try:
        host,port = hostport.replace('http://','').replace('https://','').split(':')
        s=socket.create_connection((host,int(port)),timeout=2); s.close(); return "REACHABLE"
    except Exception as e:
        return f"ERROR:{str(e)}"
out={}
out["s3_primary"]=can_connect(os.getenv("S3_PRIMARY_ENDPOINT"))
out["s3_secondary"]=can_connect(os.getenv("S3_SECONDARY_ENDPOINT"))
print(json.dumps(out))
PY
```

6. Final decision (agent must synthesize into `/reports/G.2_precheck.json`)

```bash
python - <<'PY' > /reports/G.2_precheck.json 2>&1
import json,glob
def read_jsonp(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return {}
r={}
r.update(read_jsonp("reports/logs/G.2_precheck_registry.log") or {})
r.update({"postgres": read_jsonp("reports/logs/G.2_precheck_postgres.log")})
r.update(read_jsonp("reports/logs/G.2_precheck_vault_cosign.log") or {})
r.update(read_jsonp("reports/logs/G.2_precheck_cloud.log") or {})
decision="BLOCK"
# simple rule:
reg = r.get("registry","UNKNOWN")
pri = r.get("postgres",{}).get("primary","MISSING") if isinstance(r.get("postgres",{}),dict) else "MISSING"
if reg.startswith("UP") and pri=="REACHABLE":
    decision="PROCEED"
elif reg.startswith("UP"):
    decision="PROCEED_SIMULATION"
else:
    decision="BLOCK"
out={"registry":reg,"postgres":r.get("postgres",{}),"vault":r.get("vault","MISSING"),"cosign":r.get("cosign","MISSING"),"decision":decision}
print(json.dumps(out,indent=2))
PY
```

---

## Agent rules

* If decision == BLOCK create file `/reports/PhaseG.2_precheck_block.txt` with details and stop.
* If decision == PROCEED_SIMULATION set `SIMULATION_MODE=true` in environment for subsequent steps.
* Always attach these outputs to the task report.

End of precheck.