#!/usr/bin/env bash
set -e
REPORTS="reports/k7"
mkdir -p "${REPORTS}"
COUNT=${PARTNER_BETA_COUNT:-3}
echo "Seeding ${COUNT} partner test entries (SIMULATION_MODE=${SIMULATION_MODE:-true})"
for i in $(seq 1 ${COUNT}); do
  id="partner-test-${i}"
  cat > "${REPORTS}/${id}.json" <<JSON
{
  "partner_id":"${id}",
  "name":"Partner ${i}",
  "email":"partner${i}@example.com",
  "org":"PartnerOrg${i}",
  "status":"pre-seeded"
}
JSON
done
echo "Seeded partners in ${REPORTS}"