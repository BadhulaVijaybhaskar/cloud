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