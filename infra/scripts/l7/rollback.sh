#!/bin/bash
set -euo pipefail
echo '{"phase":"L.7","rollback":"simulated"}' > reports/l7/rollback_summary.json
echo "rollback simulated"
