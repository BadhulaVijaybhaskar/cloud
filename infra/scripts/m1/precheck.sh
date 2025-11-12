#!/bin/bash
set -e

echo "Precheck for m1-global-certification"

# basic checks
command -v docker >/dev/null || echo "docker not present - simulation ok"
test -d services || { echo "services/ missing"; exit 1; }

# check keys
if [ -f infra/security/gca/signing_key.pem.sample ]; then
  echo "Signing key sample found"
else
  echo "No signing key sample found; creation recommended"
fi

# write minimal precheck report
mkdir -p reports/m1
cat > reports/m1/precheck_report.json <<'JSON'
{
  "phase":"M.1",
  "timestamp":"'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'",
  "simulation_mode": true,
  "checks":{"services_dir":"present","signing_key_sample":"present_or_missing"}
}
JSON

echo "Precheck complete"