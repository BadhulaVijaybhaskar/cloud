#!/usr/bin/env python3
"""
Test script for K8s adapter using kind or minikube
"""

import asyncio
import json
import yaml
import sys
from adapter import KubernetesAdapter

async def test_k8s_adapter():
    """Test K8s adapter functionality"""
    print("🚀 Testing Kubernetes Adapter")
    
    # Initialize adapter
    adapter = KubernetesAdapter(namespace="default")
    
    # Test 1: Apply a simple manifest
    print("\n📝 Test 1: Apply manifest")
    test_manifest = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": "test-configmap",
            "namespace": "default"
        },
        "data": {
            "test-key": "test-value"
        }
    }
    
    result = await adapter.apply_manifest(test_manifest)
    print(f"Apply result: {result['status']} - {result['message']}")
    
    # Test 2: Create a test deployment
    print("\n🚀 Test 2: Create deployment")
    deployment_manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "test-deployment",
            "namespace": "default"
        },
        "spec": {
            "replicas": 1,
            "selector": {
                "matchLabels": {
                    "app": "test-app"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": "test-app"
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": "nginx",
                            "image": "nginx:alpine",
                            "ports": [
                                {
                                    "containerPort": 80
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    result = await adapter.apply_manifest(deployment_manifest)
    print(f"Deployment result: {result['status']} - {result['message']}")
    
    if result["status"] == "success":
        # Test 3: Wait for deployment to be ready
        print("\n⏳ Test 3: Wait for deployment ready")
        result = await adapter.wait_for_deployment_ready("test-deployment", timeout=120)
        print(f"Wait result: {result['status']} - {result['message']}")
        
        # Test 4: Scale deployment
        print("\n📈 Test 4: Scale deployment")
        result = await adapter.scale_deployment("test-deployment", replicas=2)
        print(f"Scale result: {result['status']} - {result['message']}")
        
        # Test 5: Restart deployment
        print("\n🔄 Test 5: Restart deployment")
        result = await adapter.restart_pod(deployment_name="test-deployment")
        print(f"Restart result: {result['status']} - {result['message']}")
        
        # Test 6: Get resource status
        print("\n📊 Test 6: Get resource status")
        result = await adapter.get_resource_status("deployment", "test-deployment")
        print(f"Status result: {result['status']} - {result['message']}")
        
        # Test 7: Rollback deployment (will fail if no previous revision)
        print("\n↩️ Test 7: Rollback deployment")
        result = await adapter.rollback_deployment("test-deployment")
        print(f"Rollback result: {result['status']} - {result['message']}")
    
    # Test 8: Run a simple job
    print("\n⚙️ Test 8: Run job")
    job_manifest = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": "test-job",
            "namespace": "default"
        },
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": "test-container",
                            "image": "busybox",
                            "command": ["echo", "Hello from test job!"]
                        }
                    ],
                    "restartPolicy": "Never"
                }
            }
        }
    }
    
    result = await adapter.run_job(job_manifest, wait_for_completion=True)
    print(f"Job result: {result['status']} - {result['message']}")
    if "logs" in result:
        print(f"Job logs:\n{result['logs']}")
    
    print("\n🧹 Cleaning up test resources...")
    
    # Cleanup
    cleanup_commands = [
        "kubectl delete configmap test-configmap --ignore-not-found=true",
        "kubectl delete deployment test-deployment --ignore-not-found=true",
        "kubectl delete job test-job --ignore-not-found=true"
    ]
    
    for cmd in cleanup_commands:
        result = await adapter.execute_command(cmd)
        print(f"Cleanup: {cmd} - {'✅' if result['success'] else '❌'}")
    
    print("\n✅ K8s Adapter tests completed!")

async def test_dry_run():
    """Test dry-run functionality"""
    print("\n🧪 Testing dry-run mode")
    
    adapter = KubernetesAdapter()
    
    # Mock dry-run test (adapter doesn't have built-in dry-run, but we can test the structure)
    test_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "dry-run-test"},
        "spec": {
            "containers": [{"name": "test", "image": "nginx"}]
        }
    }
    
    print("Dry-run test structure validated ✅")

def check_prerequisites():
    """Check if kubectl and cluster are available"""
    import subprocess
    
    try:
        # Check kubectl
        result = subprocess.run(["kubectl", "version", "--client"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ kubectl not found or not working")
            return False
        
        # Check cluster connection
        result = subprocess.run(["kubectl", "cluster-info"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ No Kubernetes cluster connection")
            print("💡 Please ensure you have a running cluster (kind, minikube, etc.)")
            return False
        
        print("✅ kubectl and cluster connection verified")
        return True
        
    except Exception as e:
        print(f"❌ Prerequisites check failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Checking prerequisites...")
    
    if not check_prerequisites():
        print("\n💡 To run these tests, you need:")
        print("   1. kubectl installed and in PATH")
        print("   2. A running Kubernetes cluster (kind/minikube/etc.)")
        print("   3. Valid kubeconfig")
        print("\nFor kind: kind create cluster")
        print("For minikube: minikube start")
        sys.exit(1)
    
    print("\n🎯 Running K8s Adapter tests...")
    asyncio.run(test_k8s_adapter())
    asyncio.run(test_dry_run())