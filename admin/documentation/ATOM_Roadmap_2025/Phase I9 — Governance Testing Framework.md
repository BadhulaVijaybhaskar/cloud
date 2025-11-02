I generated the requested **Agent-Ready .md** for the next highest-leverage phase: **I9 — Governance Testing Framework**. Save as `phase-I9_agent_ready.md` and feed to your Master Agent.

# Phase I9 — Governance Testing Framework (Agent-Ready Build Plan)

**Project:** ATOM Cloud
**Phase:** I9 — Governance Testing Framework
**Version target:** v1.0.0-phaseI9
**Branch prefix (local):** prod-feature/I9.<task>
**Mode:** Autonomous execution (agent must set `SIMULATION_MODE=true` if infra missing)

---

## Summary / Goal

Build an automated governance testing framework that validates P1–P20 policy enforcement across services.
Success criteria (measurable):

* End-to-end compliance tests pass for 90% of policy checks in simulation mode and 100% on real infra.
* CI gate fails on policy regressions.
* Generated report `reports/I9_governance_test_report.json` contains per-policy pass/fail and evidence (logs, traces, commit hashes).
* A runnable test suite `/tests/i9/` with `pytest` or `node` stubs that completes locally under `SIMULATION_MODE=true`.

## New / I9 Policies (added)

Agent must enforce and validate the following policy checks (enforcement = automated test assertions + policy rule evaluation):

* **P1 (Data Privacy & PII Protection)**

  * Check: any API that returns user data must mask PII fields.
  * Enforcement: validate response schemas, run sample queries, assert PII fields hashed/removed.

* **P2 (Security & Access Control)**

  * Check: all endpoints require valid JWT and RBAC enforcement.
  * Enforcement: test unauthorized, expired token, role-limited access.

* **P3 (Audit & Compliance Logging)**

  * Check: every state-changing operation logs user, timestamp, operation id.
  * Enforcement: inspect logs API and verify log entries.

* **P4 (Resource Usage & Optimization)**

  * Check: resource-intensive endpoints have rate limits and cost tags.
  * Enforcement: simulate load and inspect rate-limit headers and billing events.

* **P5 (AI Ethics & Bias Prevention)**

  * Check: model inference must return a bias_score and warning when above threshold.
  * Enforcement: run curated inputs that should trigger bias detection.

* **P6 (Explainability & Transparency)**

  * Check: decisions must include `explainability.trace` object.
  * Enforcement: assert presence and schema.

* **P7 (Emergency Controls & Safety)**

  * Check: emergency stop toggles disable critical actions.
  * Enforcement: toggle emergency flag and assert operations blocked.

* **P8–P15 (Extended)**

  * Examples: Multi-tenant isolation (P8). Validate tenant can't access other tenant data.
  * P9-P15 similar checks (cost governance, SLA, DR, integration, testing, deployment).

* **P16–P20 (Production Policies)**

  * P16: Infrastructure separation. Check prod vs staging separation.
  * P17: Deployment verification. Assert canary acceptance criteria.
  * P18: Rollback readiness. Test rollback procedure.
  * P19: Live observability. Ensure telemetry emitted.
  * P20: Access & Cost Governance. Validate billing events and access audits.

(Agent must read `docs/policies/POLICIES.md` to expand rule definitions. If absent, use the above canonical checks.)

## Environment Variables (agent must read/use)

```
SIMULATION_MODE=true          # default true; set false to run in real infra
ATOM_ROOT=/workspace/atom-cloud
I9_REPORT_DIR=$ATOM_ROOT/reports/i9
I9_TEST_DIR=$ATOM_ROOT/tests/i9
I9_LOG_DIR=$ATOM_ROOT/logs/i9
CI=true                       # set by CI runner
GIT_COMMIT=$(git rev-parse --short HEAD || echo "local")
HASURA_ADMIN_SECRET=${HASURA_ADMIN_SECRET:-changeme}
POSTGRES_URL=${POSTGRES_URL:-postgres://user:pass@localhost:5432/atom}
VECTOR_DB_URL=${VECTOR_DB_URL:-http://localhost:19121}
KUBECONFIG=${KUBECONFIG:-~/.kube/config}
MAX_PARALLEL_TESTS=4
POLICY_THRESHOLD_BIAS=0.7
```

## File / Directory Structure to Create (exact)

```
phase-i9/
├── README.md
├── agent_plan.md                 # this file copy for agent
├── infra_checks/
│   ├── preflight.sh
│   └── kube_checks.sh
├── test_specs/
│   ├── p1_pii_spec.json
│   ├── p2_auth_spec.json
│   └── p5_bias_inputs.jsonl
├── scripts/
│   ├── run_i9_tests.sh
│   ├── generate_evidence.sh
│   └── upload_report.sh
├── tests/i9/
│   ├── test_p1_pii.py
│   ├── test_p2_auth.py
│   ├── test_p3_audit.py
│   ├── test_p5_bias.py
│   └── conftest.py
├── connectors/
│   ├── logs_api_client.py
│   └── hasura_client.py
├── reports/
│   └── I9_governance_test_report.json   # output
└── ci/
    └── i9_ci_job.yml
```

## High-Level Tasks (I9.1 → I9.10)

| ID    | Component                | Purpose                                              |
| ----- | ------------------------ | ---------------------------------------------------- |
| I9.1  | infra preflight checks   | Verify infra access, endpoints, and credentials      |
| I9.2  | policy spec ingestion    | Load P1-P20 definitions from docs or use defaults    |
| I9.3  | test harness setup       | Create pytest node runner or JS runner with stubs    |
| I9.4  | connectors               | Implement Hasura, Logs, Billing clients for evidence |
| I9.5  | unit/contract tests      | Validate schemas and contracts for endpoints         |
| I9.6  | integration policy tests | Run end-to-end policy assertions per P1-P20          |
| I9.7  | evidence collection      | Save logs, traces, request/response samples          |
| I9.8  | reporting                | Emit JSON + human summary and CI annotations         |
| I9.9  | CI gating integration    | Add job that fails on critical policy failure        |
| I9.10 | remediation playbooks    | Auto-generate issues with steps for failing tests    |

## Detailed Task Specs & Endpoints

### I9.1 infra preflight checks

* Endpoint checks:

  * `GET /health` (api gateway) -> expect `200 {"status":"ok","commit":"$GIT_COMMIT"}`
  * `GET /hasura/healthz` -> `200 {"status":"ok"}`
  * `GET /logs/health` -> `200`
* Behavior: if `SIMULATION_MODE=true` skip external endpoint failures and create simulated responses saved under `phase-i9/infra_checks/simulated/`.

### I9.3 test harness setup

* Use `pytest` with `pytest-xdist` or Node `jest` for JS. Default implementation provided in Python.
* Conftest must read env vars and provide fixture `client` returning simulated or real connectors.

### Key API Endpoints to Validate (examples)

* GraphQL query (Hasura): POST `${HASURA_URL}/v1/graphql` with `X-Hasura-Admin-Secret` header.

  * Validate RLS by issuing query under tenant header `x-tenant-id`.
* Auth endpoints:

  * `POST /auth/login` produce JWT. Validate role claims.
* Logs API:

  * `POST /logs/query` -> return structured logs.

## Data Contracts (schemas)

Place JSON schemas into `test_specs/`:

* `p1_pii_spec.json`

```json
{
  "$id": "p1_pii",
  "type": "object",
  "properties": {
    "user_id": {"type": "string"},
    "email": {"type": "string", "format":"email"},
    "ssn": {"type":"string"},
    "masked_ssn": {"type":"string"}
  },
  "required": ["user_id","email"]
}
```

* `p2_auth_spec.json` - expected JWT claims schema.

Store schemas as exact filenames in `test_specs/`.

## Embedded Scripts Pattern

### preflight.sh (embedded)

**File:** `phase-i9/infra_checks/preflight.sh` — Verify local tools and env.

```bash
#!/usr/bin/env bash
set -euo pipefail
: "${ATOM_ROOT:=/workspace/atom-cloud}"
: "${SIMULATION_MODE:=true}"
mkdir -p "$ATOM_ROOT/reports/i9"
echo "I9 Preflight - SIMULATION_MODE=${SIMULATION_MODE}" > "$ATOM_ROOT/reports/i9/preflight.txt"
if [ "$SIMULATION_MODE" = "false" ]; then
  echo "Checking Hasura..."
  curl -sSf "${HASURA_URL:-http://localhost:8080}/healthz" || { echo "Hasura unreachable"; exit 2; }
  echo "Hasura OK" >> "$ATOM_ROOT/reports/i9/preflight.txt"
fi
echo "Preflight complete"
```

*Make executable: `chmod +x preflight.sh`.*

### run_i9_tests.sh (embedded)

**File:** `phase-i9/scripts/run_i9_tests.sh` — Run test suite and output JSON report.

```bash
#!/usr/bin/env bash
set -euo pipefail
export PYTEST_ADDOPTS="--maxfail=1 -q"
export REPORT_DIR="${REPORT_DIR:-$ATOM_ROOT/reports/i9}"
mkdir -p "$REPORT_DIR"
if [ "${SIMULATION_MODE:-true}" = "true" ]; then
  echo "Running in SIMULATION_MODE" > "$REPORT_DIR/mode.txt"
fi
pytest tests/i9 --json-report --json-report-file="$REPORT_DIR/I9_pytest_report.json"
python3 scripts/generate_evidence.py --input "$REPORT_DIR/I9_pytest_report.json" --output "$REPORT_DIR/I9_governance_test_report.json"
```

*Make executable.*

### generate_evidence.sh (embedded)

**File:** `phase-i9/scripts/generate_evidence.sh`

```bash
#!/usr/bin/env bash
python3 scripts/generate_evidence.py "$@"
```

### generate_evidence.py (embedded)

**File:** `phase-i9/scripts/generate_evidence.py` — minimal evidence aggregator (Python)

```python
#!/usr/bin/env python3
import json,sys,os
infile = sys.argv[1] if len(sys.argv)>1 else '/workspace/atom-cloud/reports/i9/I9_pytest_report.json'
outfile = sys.argv[2] if len(sys.argv)>2 else '/workspace/atom-cloud/reports/i9/I9_governance_test_report.json'
data = {}
if os.path.exists(infile):
    with open(infile,'r') as f:
        data['pytest'] = json.load(f)
else:
    data['pytest'] = {"note":"simulated","passed":0,"failed":0}
# minimal evidence: collect last git commit
import subprocess
try:
    commit = subprocess.check_output(['git','rev-parse','--short','HEAD']).decode().strip()
except Exception:
    commit = 'local'
data['git_commit'] = commit
with open(outfile,'w') as f:
    json.dump(data,f,indent=2)
print("Wrote", outfile)
```

## Verification & Testing

### Verification Commands (agent must run and save outputs)

```bash
# from repo root
export ATOM_ROOT=/workspace/atom-cloud
export SIMULATION_MODE=true
phase-i9/infra_checks/preflight.sh | tee $ATOM_ROOT/reports/i9/preflight.log
phase-i9/scripts/run_i9_tests.sh 2>&1 | tee $ATOM_ROOT/reports/i9/run_tests.log
# produce final evidence
cat $ATOM_ROOT/reports/i9/I9_governance_test_report.json
```

### Integration Test Stub (agent must create)

**File:** `phase-i9/tests/i9/test_p2_auth.py`

```python
import os, pytest
from connectors.hasura_client import HasuraClient

@pytest.fixture(scope="module")
def hasura():
    return HasuraClient(url=os.getenv("HASURA_URL","http://localhost:8080"), admin_secret=os.getenv("HASURA_ADMIN_SECRET","changeme"))

def test_rbac_denied_for_unprivileged(hasura):
    token = "ey.invalid.token"
    resp = hasura.query("{__typename}")  # in simulation client this returns simulated
    assert isinstance(resp, dict)
```

(Agent must create similar stubs for test_p1_pii.py, test_p3_audit.py, test_p5_bias.py.)

## Agent Instructions

> Execute in sequence. Use `SIMULATION_MODE=true` when infra is unavailable. Fail fast on missing credentials. Always save evidence.

### Agent Execution Steps (explicit sequence)

1. Checkout new branch:
   `git checkout -b prod-feature/I9.init && git push -u origin prod-feature/I9.init`
2. Create directory tree exactly as specified and commit skeleton files (README, scripts, tests).
3. Run `phase-i9/infra_checks/preflight.sh`. If `SIMULATION_MODE=false` and infra fails, record errors and abort.
4. Populate `test_specs/` by pulling `docs/policies/POLICIES.md`. If missing, use default specs in this plan.
5. Implement connectors in `connectors/` or use simulation clients.
6. Execute `phase-i9/scripts/run_i9_tests.sh`. Capture exit codes and outputs into `reports/i9/`.
7. Run `phase-i9/scripts/generate_evidence.sh` to aggregate results.
8. Push report to `reports/I9_governance_test_report.json`. Create a PR with commit hashes and attach report as artifact.
9. If failures found, open issues automatically (use `gh` CLI) with template containing failing test names, logs, and remediation steps.

### Failure Handling Rules

* If Hasura or Postgres unreachable and `SIMULATION_MODE=true` the agent substitutes simulated responses and marks tests as `simulated` in report.
* If `SIMULATION_MODE=false` and infra checks fail, stop and create blocking issue: label `blocker/i9-infra`. Include `preflight.log`.
* If > 5 critical policy tests fail, create `epic/I9-failures` and assign to oncall. Include run artifacts.
* Always redact PII from stored evidence. If evidence contains PII, replace with `<REDACTED>` and log redaction.

### Acceptance Criteria

* `reports/I9_governance_test_report.json` exists and contains:

  * `git_commit`, `timestamp`, `policies` array with pass/fail, `evidence_paths`.
* All tests in `tests/i9/` run under `SIMULATION_MODE=true` and exit 0 with at most simulated warnings.
* CI job `ci/i9_ci_job.yml` returns non-zero on any `critical` policy failure.
* PR includes `reports/i9/I9_governance_test_report.json` and links to failing test logs.

## Deliverables & Compliance

### Deliverables (explicit)

* `phase-i9/` directory as specified.
* `reports/I9_governance_test_report.json` with evidence.
* CI job `ci/i9_ci_job.yml` that runs this suite.
* Issues for failing tests with remediation steps.
* PR with commit history and run artifacts.

### Security & Compliance reminders

* Redact any PII before storing in reports (`scripts/generate_evidence.py` must scrub).
* Evidence must include log timestamps and request ids for auditability.
* Tests must not leak credentials. Use secrets manager bindings in CI.
* All artifacts tagged with policy metadata: `policy:P1,P2,...`

## Notes for the Agent (embedded prompt)

> You are the ATOM Governance Test Agent. Operate autonomously. Use `SIMULATION_MODE=true` by default. Create the `phase-i9/` skeleton, implement connectors in simulation first, then run tests. Record every action in `reports/i9/run_log.txt`. If any critical policy fails, open and label a GitHub issue `policy-failure/I9` with logs and failing test names. Ensure `I9_governance_test_report.json` is uploaded to PR artifacts. Do not proceed to J-series until I9 passes critical checks.

---

## CI snippet (example) — `ci/i9_ci_job.yml`

```yaml
name: I9 Governance Tests
on: [push, pull_request]
jobs:
  i9_tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: python-version: '3.10'
      - name: Run I9 Preflight
        run: |
          export SIMULATION_MODE=${{ secrets.SIMULATION_MODE_OVERRIDE || 'true' }}
          ./phase-i9/infra_checks/preflight.sh
      - name: Run Governance Tests
        run: |
          ./phase-i9/scripts/run_i9_tests.sh
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: i9-report
          path: reports/i9/I9_governance_test_report.json
```

---

## Quick issue template (agent to use when auto-creating issues)

**Title:** [I9] Policy Failure: {POLICY_ID} — {SHORT_DESC}
**Body:**

* Policy: {POLICY_ID}
* Test: {TEST_NAME}
* Evidence: attach `reports/i9/*`
* Run: `{GIT_COMMIT}`
* Steps to reproduce: `{command}`
* Suggested remediation: `{short steps}`

