#!/bin/bash
set -e
mkdir -p reports/k1
echo "[K1] Precheck start" > reports/k1/precheck.log
kubectl get pods -n ${NAMESPACE:-atom-auto} --no-headers >> reports/k1/precheck.log || true
vault status >> reports/k1/precheck.log || true
echo "[K1] Precheck complete" >> reports/k1/precheck.log