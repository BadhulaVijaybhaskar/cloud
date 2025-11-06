#!/usr/bin/env bash
set -e
SRC="reports/k6"
DST="ui/launchpad/integration-dashboard/public/reports/k6"
mkdir -p "$DST"
cp -r "$SRC"/* "$DST" || true
echo "Copied reports to $DST"