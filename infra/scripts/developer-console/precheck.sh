#!/bin/bash
set -euo pipefail
: "${SIMULATION_MODE:=true}"
LAUNCHPAD_SRC_PATH="${LAUNCHPAD_SRC_PATH:-collective_intelligence/launchpad}"

# 1. Ensure no phase directories exist
if ls -d phase-* 2>/dev/null; then
  echo "ERROR: phase-* directories present. Abort." >&2
  exit 2
fi

# 2. Check LaunchPad source
mkdir -p reports
if [ -d "${LAUNCHPAD_SRC_PATH}" ]; then
  echo "FOUND_LAUNCHPAD" >&2
  find "${LAUNCHPAD_SRC_PATH}" -maxdepth 3 -type f | sed "s|^|${LAUNCHPAD_SRC_PATH}/|" > reports/launchpad_ui_filelist.txt
  wc -l reports/launchpad_ui_filelist.txt >&2
else
  echo "NO_LAUNCHPAD" >&2
fi

# 3. Helm lint (non-blocking)
if [ -d "infra/helm/developer-console" ]; then
  helm lint infra/helm/developer-console || echo "helm lint warnings"
fi

# 4. Terraform plan (simulation-only)
if [ -d "infra/terraform/modules/developer-console" ]; then
  terraform -chdir=infra/terraform/modules/developer-console init -input=false -backend=false || true
  terraform -chdir=infra/terraform/modules/developer-console plan -input=false -out=reports/developer_console.tfplan || true
fi

echo "PRECHECK_COMPLETE" >&2