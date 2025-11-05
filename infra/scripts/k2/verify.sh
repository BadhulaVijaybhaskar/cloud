#!/bin/bash
# Wrapper script for K.2 verification
# Executes "make k2-verify" to validate generated JSON reports.

set -e
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo ">>> Running K.2 verification sequence ..."
make k2-verify

echo ">>> K.2 verification complete. Check reports/k2/verification_summary.json"