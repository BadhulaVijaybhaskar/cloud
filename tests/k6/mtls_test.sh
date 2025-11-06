#!/usr/bin/env bash
set -euo pipefail
REPORT_DIR="${1:-reports/k6}"
mkdir -p "${REPORT_DIR}"
OUT="${REPORT_DIR}/mtls_handshake.json"
HOSTS=( "localhost:8901" )

echo '{"checks": [' > "$OUT"
first=true
for h in "${HOSTS[@]}"; do
  host="${h%%:*}"
  port="${h##*:}"
  set +e
  out=$(echo | openssl s_client -connect "${host}:${port}" -brief 2>&1)
  rc=$?
  set -e
  status="fail"
  if [ $rc -eq 0 ]; then status="ok"; fi
  if [ "$first" = true ]; then first=false; else echo ',' >> "$OUT"; fi
  cat >> "$OUT" <<JSON
  {"host":"${host}","port":${port},"status":"${status}","rc":${rc},"snippet":"$(echo "$out" | head -n 6 | tr '\n' ' ' | sed 's/"/\\"/g')"}
JSON
done
echo ']}' >> "$OUT"
echo "Wrote $OUT"