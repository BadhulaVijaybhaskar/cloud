# Compliance Precheck — Phase I.6 Adaptive Optimization Readiness

**Purpose:** verify infra readiness for Adaptive Optimization Layer (AOL)  
**Output:** `/reports/I.6_precheck.json` and `/reports/logs/I.6_precheck.log`

---

### ✅ Steps

1. **Prepare directories**

```bash
mkdir -p reports/logs
```

2. **Capture environment**

```bash
env | grep -E 'POSTGRES_DSN|PROM_URL|JAEGER_URL|VAULT_ADDR|COSIGN_KEY_PATH|NEURAL_FABRIC_URL|GLOBAL_ROUTER_URL|POLICY_ENGINE_URL|MODEL_STORE_URL|SIMULATION_MODE' \
> reports/logs/I.6_precheck_env.txt
```

3. **Python check script**

```bash
python - <<'PY' > reports/logs/I.6_precheck.json
import os, json, requests, time

fields = ["POSTGRES_DSN","PROM_URL","JAEGER_URL","VAULT_ADDR","COSIGN_KEY_PATH",
          "NEURAL_FABRIC_URL","GLOBAL_ROUTER_URL","POLICY_ENGINE_URL","MODEL_STORE_URL"]
out = {}
for f in fields:
    out[f] = "SET" if os.getenv(f) else "MISSING"

def health(url):
    try:
        r = requests.get(url+"/health", timeout=3)
        return "UP" if r.ok else f"DOWN:{r.status_code}"
    except Exception as e:
        return f"ERR:{e.__class__.__name__}"

for k in ["POLICY_ENGINE_URL","MODEL_STORE_URL","GLOBAL_ROUTER_URL","NEURAL_FABRIC_URL"]:
    u = os.getenv(k)
    if u: out[f"check_{k}"] = health(u)

decision = "PROCEED"
if any(out[v]=="MISSING" for v in ["POSTGRES_DSN","POLICY_ENGINE_URL","MODEL_STORE_URL"]):
    decision = "PROCEED_SIMULATION"
if out.get("VAULT_ADDR")=="MISSING" and out.get("COSIGN_KEY_PATH")=="MISSING":
    decision = "PROCEED_SIMULATION"
out["SIMULATION_MODE"] = os.getenv("SIMULATION_MODE","true")
out["decision"] = decision
out["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
json.dump(out, open("reports/I.6_precheck.json","w"), indent=2)
print(json.dumps(out, indent=2))
PY
```

4. **Interpretation**

| Decision             | Meaning                                              |
| -------------------- | ---------------------------------------------------- |
| `PROCEED`            | All critical infra available — run in live test mode |
| `PROCEED_SIMULATION` | Some infra missing — force `SIMULATION_MODE=true`    |
| `BLOCK`              | Cannot continue; essential systems unreachable       |

---

### ✅ Agent Task

If `"decision"` == `"PROCEED_SIMULATION"` → export `SIMULATION_MODE=true` and proceed.
Otherwise → continue normally.