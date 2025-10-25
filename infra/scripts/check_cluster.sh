#!/bin/bash
echo "Checking cluster state..."
kubectl get nodes -o wide
echo
kubectl get ns
echo
kubectl get componentstatuses
echo
kubectl get pods -A | grep -v "Running"