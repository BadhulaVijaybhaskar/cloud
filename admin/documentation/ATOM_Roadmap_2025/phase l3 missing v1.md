Each one is a **post-blocker hardening step**—not required for launch, but ensures long-term stability and compliance for L.3 in production.
Here’s what each means in plain operational terms:

---

### 1. **Automated CI Check (`.github/workflows/l3_blocker_check.yml`)**

**Purpose:**
Prevents accidental merges or deployments unless all required reports and approvals exist.

**Mechanism:**
A GitHub Actions workflow runs automatically on pull requests.
It checks that key files such as:

* `reports/l3/precheck_report.json`
* `reports/l3/deploy_summary.json`
* `reports/l3/approval_signoffs.json`
  exist and contain `"status": "PASS"` or valid signatures.

**Outcome:**
Ensures no one merges an incomplete L.3 change into `main` without simulation and signoff evidence.

---

### 2. **Artifact Retention (S3 Archival for logs/reports)**

**Purpose:**
Retains historical evidence and audit logs required by governance policies (P28–P31).

**Mechanism:**
A cron or GitHub Actions job uploads all `reports/l3/*.log` and `reports/l3/*.json` to an S3 bucket nightly:

```
s3://atom-audit-archive/l3/YYYY/MM/DD/
```

Retention is set to **30 days**, after which older logs auto-expire.

**Outcome:**
Maintains audit continuity and traceability even after local cleanup or CI artifact expiry.

---

### 3. **Vault Test Account (PKI + Policy Verification)**

**Purpose:**
Validates that Vault production secrets, policies, and PKI certificate issuance work before live deployment.

**Mechanism:**
Create a dedicated “test” service identity (e.g., `svc-l3-test`):

```bash
vault token create -policy=l3-gae-readonly -ttl=30m
vault write pki/issue/l3-pki-role common_name="test.atom.internal"
```

Then verify that:

* Tokens can read expected secrets.
* PKI issues valid, policy-bound certificates.

**Outcome:**
Confirms live Vault configuration matches simulation and prevents authentication errors post-launch.

---

### 4. **Alert Dry-Run (PagerDuty/Slack Validation)**

**Purpose:**
Ensures the monitoring and alerting setup actually pages the right team when an issue occurs.

**Mechanism:**
Simulate a `L3ServiceDown` alert:

```bash
kubectl scale deploy l3-orchestrator -n l3-gae --replicas=0
```

Wait 2–3 minutes until Prometheus triggers the alert.
Confirm PagerDuty or Slack receives it per `docs/on_call_roster.md`.

**Outcome:**
Verifies full alerting loop — from Prometheus alert → Alertmanager → PagerDuty/Slack → operator response.

---

### Summary

| Step               | Purpose                          | When to Run   | Effect                 |
| ------------------ | -------------------------------- | ------------- | ---------------------- |
| CI blocker check   | Enforce evidence before PR merge | Every PR      | Governance automation  |
| Artifact retention | Preserve audit logs              | Nightly       | Long-term traceability |
| Vault test account | Validate PKI + policies          | Before live   | Security assurance     |
| Alert dry-run      | Verify paging & alerts           | Before canary | Operational confidence |

---

Nice — I’ll generate the four automation artifacts now so you can drop them into the repo and run them immediately. Below are the exact file paths and full contents for each file. All scripts are simulation-safe by default (they respect `SIMULATION_MODE=true`) and include comments and usage examples.

---

# 1) GitHub Actions: `.github/workflows/l3_blocker_check.yml`

**Purpose:** CI pre-merge blocker: ensures required L.3 evidence files exist and assert PASS-like status before allowing merge.

```yaml
name: L3 Blocker Check

on:
  pull_request:
    paths:
      - 'reports/l3/**'
      - '.github/workflows/**'
      - 'infra/**'
      - 'docs/**'

jobs:
  l3_blocker_check:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install jq
        run: sudo apt-get update -y && sudo apt-get install -y jq

      - name: Check required files exist
        run: |
          REQUIRED=(
            "reports/l3/precheck_report.json"
            "reports/l3/deploy_summary.json"
            "reports/l3/verification_summary.json"
            "reports/l3/approval_signoffs.json"
          )
          MISSING=0
          for f in "${REQUIRED[@]}"; do
            if [ ! -f "$f" ]; then
              echo "ERROR: required file missing -> $f"
              MISSING=1
            else
              echo "FOUND: $f"
            fi
          done
          if [ "$MISSING" -eq 1 ]; then
            echo "::error file=./l3_blocker_check::One or more required L.3 report files are missing."
            exit 1
          fi

      - name: Validate reports contain PASS/OK
        run: |
          fail=0
          for f in reports/l3/*.json; do
            if jq -e '(.overall_status // .status // .result // .overall_result) | test("PASS|OK|SIM_OK|PASS_SIMULATION")' "$f" >/dev/null 2>&1; then
              echo "OK: $f reports PASS-like status"
            else
              echo "WARN/FAIL: $f does not contain PASS-like status (searching keys overall_status/status/result/overall_result)"
              jq '.' "$f" || true
              fail=1
            fi
          done
          if [ "$fail" -ne 0 ]; then
            echo "::error file=./l3_blocker_check::One or more L.3 reports are not PASS-like."
            exit 1
          fi

      - name: Check approvals signature entries
        run: |
          if [ -f reports/l3/approval_signoffs.json ]; then
            cnt=$(jq '.signoffs|length' reports/l3/approval_signoffs.json 2>/dev/null || echo "0")
            echo "approval_signoffs.json signoff entries: $cnt"
            if [ "$cnt" -lt 1 ]; then
              echo "::warning::approval_signoffs.json exists but has no signoffs recorded."
            fi
          else
            echo "::warning::approval_signoffs.json missing (should be created by release runbooks)."
          fi

      - name: Upload artifact (evidence)
        uses: actions/upload-artifact@v4
        with:
          name: l3_evidence
          path: reports/l3
```

---

# 2) Artifact retention uploader: `infra/scripts/l3/archive_reports_to_s3.sh`

**Purpose:** nightly archival of `reports/l3/*` to an S3 bucket with 30-day retention. Simulation-safe; if `SIMULATION_MODE=true` it will only show what it would upload.

```bash
#!/usr/bin/env bash
set -euo pipefail
# infra/scripts/l3/archive_reports_to_s3.sh
#
# Upload reports/l3/* -> S3 archival path
# Respect SIMULATION_MODE=true by default (safe).
#
# Required environment:
#   AWS CLI configured with credentials and region
#   S3_BUCKET (e.g. atom-audit-archive)
#
# Usage:
#   SIMULATION_MODE=true ./archive_reports_to_s3.sh
#   SIMULATION_MODE=false S3_BUCKET=atom-audit-archive ./archive_reports_to_s3.sh

SIMULATION_MODE="${SIMULATION_MODE:-true}"
S3_BUCKET="${S3_BUCKET:-atom-audit-archive}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
DATE_PATH=$(date -u +"%Y/%m/%d")
SRC_DIR="reports/l3"
DEST_PREFIX="l3/${DATE_PATH}"

echo "Archive script starting. SIMULATION_MODE=${SIMULATION_MODE}"
echo "Source: ${SRC_DIR}"
echo "Destination: s3://${S3_BUCKET}/${DEST_PREFIX}"
echo "Retention (days): ${RETENTION_DAYS}"

if [ ! -d "${SRC_DIR}" ]; then
  echo "No reports directory found at ${SRC_DIR} — nothing to archive."
  exit 0
fi

if [ "${SIMULATION_MODE}" = "true" ]; then
  echo "[SIMULATION] Would upload files:"
  find "${SRC_DIR}" -type f -maxdepth 1 -print
  echo "[SIMULATION] Command sample:"
  echo "aws s3 cp ${SRC_DIR}/ <s3://$S3_BUCKET/$DEST_PREFIX/> --recursive"
  exit 0
fi

# Real upload
aws s3 cp "${SRC_DIR}/" "s3://${S3_BUCKET}/${DEST_PREFIX}/" --recursive --acl bucket-owner-full-control
echo "Uploaded reports to s3://${S3_BUCKET}/${DEST_PREFIX}/"

# Apply lifecycle via tagging (example: add lifecycle via bucket policy outside script),
# here we add an object tag marking retention days (many shops manage lifecycle at bucket level).
for f in $(find "${SRC_DIR}" -type f -maxdepth 1); do
  fname=$(basename "$f")
  aws s3api put-object-tagging --bucket "${S3_BUCKET}" --key "${DEST_PREFIX}/${fname}" \
    --tagging "TagSet=[{Key=retention_days,Value=${RETENTION_DAYS}}]"
done

echo "Archival complete."
```

Make executable: `chmod +x infra/scripts/l3/archive_reports_to_s3.sh`

---

# 3) Vault PKI & policy test helper: `infra/scripts/l3/vault_pki_policy_test.sh`

**Purpose:** validate Vault connectivity, issue a short-lived token & cert for a test identity, and assert policy access. Simulation-safe: dry-run by default.

```bash
#!/usr/bin/env bash
set -euo pipefail
# infra/scripts/l3/vault_pki_policy_test.sh
#
# Validates Vault connectivity and PKI issuance for L.3.
#
# Environment:
#   VAULT_ADDR, VAULT_TOKEN (or use login method)
#   SIMULATION_MODE=true|false
#
# Usage:
#  SIMULATION_MODE=true ./vault_pki_policy_test.sh
#  SIMULATION_MODE=false ./vault_pki_policy_test.sh

SIMULATION_MODE="${SIMULATION_MODE:-true}"
VAULT_ADDR="${VAULT_ADDR:-https://vault.atom.internal}"
TEST_ROLE="${TEST_ROLE:-l3-test-role}"
TEST_POLICY="${TEST_POLICY:-l3_readonly}"
TEST_COMMON_NAME="${TEST_COMMON_NAME:-test.l3.local}"
TTL="${TTL:-5m}"

echo "Vault PKI & Policy test starting. SIMULATION_MODE=${SIMULATION_MODE}"
echo "VAULT_ADDR=${VAULT_ADDR}"
echo "Role=${TEST_ROLE} Policy=${TEST_POLICY} CN=${TEST_COMMON_NAME} TTL=${TTL}"

if [ "${SIMULATION_MODE}" = "true" ]; then
  echo "[SIMULATION] Would perform:"
  echo "1) vault token create -policy=${TEST_POLICY} -orphan -ttl=${TTL}"
  echo "2) vault write pki/issue/${TEST_ROLE} common_name=${TEST_COMMON_NAME} ttl=${TTL}"
  echo "3) test access to secret: vault kv get secret/l3/test (simulated)"
  exit 0
fi

# Check vault reachable
if ! curl -sSf "${VAULT_ADDR}/v1/sys/health" >/dev/null 2>&1; then
  echo "ERROR: Vault not reachable at ${VAULT_ADDR}"
  exit 1
fi
echo "Vault reachable."

# Create token with the test policy (requires appropriate privileges)
echo "Creating test token..."
tok_json=$(vault token create -policy="${TEST_POLICY}" -orphan -ttl="${TTL}" -format=json)
TEST_TOKEN=$(echo "${tok_json}" | jq -r '.auth.client_token')
echo "Test token created (short-lived)."

# Issue test certificate from PKI role
echo "Issuing test certificate..."
cert_json=$(VAULT_TOKEN="${TEST_TOKEN}" vault write -format=json pki/issue/"${TEST_ROLE}" common_name="${TEST_COMMON_NAME}" ttl="${TTL}")
echo "Certificate issued (simulated fields):"
echo "${cert_json}" | jq -r '.data | {serial_number,certificate,issuing_ca} | keys as $k | .'

# Validate test policy access (example secret read)
echo "Validating secret access with test token (read attempt)..."
if VAULT_TOKEN="${TEST_TOKEN}" vault kv get secret/l3/test >/dev/null 2>&1; then
  echo "Secret read succeeded with test token (policy binding OK)."
else
  echo "Warning: Secret read with test token failed. Confirm policies and secret path existence."
fi

echo "Vault PKI & Policy test complete. Revoke test token..."
vault token revoke "${TEST_TOKEN}" || true
echo "Done."
```

Make executable: `chmod +x infra/scripts/l3/vault_pki_policy_test.sh`

> NOTE: Running the script requires `vault` CLI installed and privileges to create tokens/issue certs. Keep `SIMULATION_MODE=true` until you are ready and have operator approvals.

---

# 4) Alert dry-run helper: `infra/scripts/l3/alert_dryrun.sh`

**Purpose:** safely trigger alert rules (dry-run) to verify Alertmanager → PagerDuty/Slack routing without impacting production services. Uses simulation toggles and optionally posts to Slack only if `DRYRUN_POST=true`.

```bash
#!/usr/bin/env bash
set -euo pipefail
# infra/scripts/l3/alert_dryrun.sh
#
# Trigger a controlled alert event to verify the alerting pipeline.
# Uses Prometheus Alertmanager HTTP API to POST a fake alert.
#
# Environment:
#   ALERTMANAGER_URL (e.g. http://alertmanager.monitoring.svc:9093)
#   SIMULATION_MODE=true|false (default true)
#   DRYRUN_POST=false|true  (if true, post to actual Alertmanager)
#
# Usage:
#   SIMULATION_MODE=true ./alert_dryrun.sh
#   SIMULATION_MODE=false DRYRUN_POST=true ALERTMANAGER_URL=http://am:9093 ./alert_dryrun.sh

ALERTMANAGER_URL="${ALERTMANAGER_URL:-http://localhost:9093}"
SIMULATION_MODE="${SIMULATION_MODE:-true}"
DRYRUN_POST="${DRYRUN_POST:-false}"

ALERT_NAME="L3ServiceDownTest"
INSTANCE="l3-orchestrator-dryrun"
SEVERITY="critical"
DESCRIPTION="Dry-run check: simulate L3 service down for alert routing verification."
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

payload=$(cat <<JSON
[
  {
    "labels": {
      "alertname": "${ALERT_NAME}",
      "severity": "${SEVERITY}",
      "instance": "${INSTANCE}",
      "team": "l3-ops"
    },
    "annotations": {
      "summary": "${DESCRIPTION}",
      "runbook": "docs/runbooks/l3_runbook.md"
    },
    "startsAt": "${TIMESTAMP}",
    "generatorURL": "https://simulator.local/l3/alert_dryrun"
  }
]
JSON
)

echo "Alert dry-run payload:"
echo "${payload}"

if [ "${SIMULATION_MODE}" = "true" ]; then
  echo "[SIMULATION] Not posting to Alertmanager. Use SIMULATION_MODE=false and DRYRUN_POST=true to actually send."
  exit 0
fi

if [ "${DRYRUN_POST}" != "true" ]; then
  echo "DRYRUN_POST is not set to true; aborting real post."
  exit 1
fi

echo "Posting to Alertmanager at ${ALERTMANAGER_URL}..."
curl -sS -XPOST -H 'Content-Type: application/json' --data "${payload}" "${ALERTMANAGER_URL}/api/v1/alerts" \
  && echo "Posted; check PagerDuty/Slack for routing." || (echo "Post failed" && exit 1)

echo "Alert dry-run complete."
```

Make executable: `chmod +x infra/scripts/l3/alert_dryrun.sh`

---

# Makefile targets (optional) — add to repo root `Makefile` to wrap these:

```makefile
.PHONY: l3-blocker-check archive-l3-s3 vault-l3-test l3-alert-dryrun

l3-blocker-check:
	@echo "Manual: GitHub Actions workflow is configured at .github/workflows/l3_blocker_check.yml"

archive-l3-s3:
	@echo "Running archival (SIMULATION_MODE=true by default)"
	@SIMULATION_MODE=true infra/scripts/l3/archive_reports_to_s3.sh

vault-l3-test:
	@echo "Vault PKI & Policy test (SIMULATION_MODE=true by default)"
	@SIMULATION_MODE=true infra/scripts/l3/vault_pki_policy_test.sh

l3-alert-dryrun:
	@echo "Alert dry-run (SIMULATION_MODE=true by default)"
	@SIMULATION_MODE=true infra/scripts/l3/alert_dryrun.sh
```

---

# How to run (quick checklist)

1. Drop files into repo:

   * `.github/workflows/l3_blocker_check.yml`
   * `infra/scripts/l3/archive_reports_to_s3.sh`
   * `infra/scripts/l3/vault_pki_policy_test.sh`
   * `infra/scripts/l3/alert_dryrun.sh`
   * (optional) update `Makefile` as above

2. Make scripts executable:

```bash
chmod +x infra/scripts/l3/*.sh
```

3. Test in simulation mode (default):

```bash
./infra/scripts/l3/archive_reports_to_s3.sh        # will print what it would upload
./infra/scripts/l3/vault_pki_policy_test.sh       # simulates vault actions
./infra/scripts/l3/alert_dryrun.sh                # prints the alert payload (no post)
```

4. To run a real archival (operator-only) — ensure AWS creds and S3 bucket:

```bash
SIMULATION_MODE=false S3_BUCKET=atom-audit-archive ./infra/scripts/l3/archive_reports_to_s3.sh
```

5. To test Alertmanager posting (operator-only):

```bash
SIMULATION_MODE=false DRYRUN_POST=true ALERTMANAGER_URL="https://alertmanager.myorg.example" ./infra/scripts/l3/alert_dryrun.sh
```

6. To run Vault test (operator-only & privileged):

```bash
SIMULATION_MODE=false VAULT_ADDR=https://vault.prod.example ./infra/scripts/l3/vault_pki_policy_test.sh
```

---


