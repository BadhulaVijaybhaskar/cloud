# Phase I.7 Precheck

Run environment checks and decide execution mode.

```bash
mkdir -p /reports/logs

# ENV check
env | grep -E 'POSTGRES_DSN|VAULT_ADDR|COSIGN_KEY_PATH|SIMULATION_MODE' > /reports/logs/I.7_precheck_env.txt 2>&1 || true

# PROM check
python - <<'PY' > /reports/logs/I.7_precheck_prom.log 2>&1
import os,requests,json
u=os.getenv('PROM_URL','http://localhost:9090')
try:
  r=requests.get(u, timeout=3)
  print(json.dumps({'prom': 'UP' if r.ok else 'DOWN'}))
except Exception as e:
  print(json.dumps({'prom': 'ERROR:'+str(e)}))
PY

# Postgres check
python - <<'PY' > /reports/logs/I.7_precheck_pg.log 2>&1
import os,json
try:
  import psycopg2
  d=os.getenv('POSTGRES_DSN')
  if not d: print(json.dumps({'postgres':'MISSING'}))
  else:
    try:
      psycopg2.connect(d,connect_timeout=3).close()
      print(json.dumps({'postgres':'REACHABLE'}))
    except Exception as e:
      print(json.dumps({'postgres':'ERROR:'+str(e)}))
except Exception as e:
  print(json.dumps({'pglib':'MISSING','error':str(e)}))
PY
```

Decision rules:

* If PROM and POSTGRES reachable and VAULT present → PROCEED
* If REGISTRY present but others missing → PROCEED_SIMULATION
* If registry/critical missing → BLOCK

Agent must write `/reports/I.7_precheck.json` with details.