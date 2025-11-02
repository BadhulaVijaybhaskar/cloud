#!/usr/bin/env python3
"""
CIN CLI - Sample commands for Phase I.5 operations
Usage: python sample_cli.py <command> [args]
"""

import sys
import json
import requests
from datetime import datetime
import uuid

# Service endpoints (adjust for your deployment)
SERVICES = {
    'signal-gateway': 'http://localhost:8001',
    'consensus-bus': 'http://localhost:8002', 
    'fl-orchestrator': 'http://localhost:8003',
    'arbiter': 'http://localhost:8004'
}

def ingest_signal(signal_type="metric", data=None):
    """Ingest a test signal"""
    if data is None:
        data = {"test": True, "value": 42}
    
    signal = {
        "signals": [{
            "signal_id": f"sig-cli-{uuid.uuid4()}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "cli-tool",
            "signal_type": signal_type,
            "data": data,
            "metadata": {
                "classification": "internal",
                "tenant_id": "cli-tenant"
            }
        }]
    }
    
    response = requests.post(
        f"{SERVICES['signal-gateway']}/v1/ingest",
        json=signal,
        headers={"Authorization": "Bearer cli-token"}
    )
    
    print(f"Signal ingestion: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def start_fl_round(participants=None):
    """Start a federated learning round"""
    if participants is None:
        participants = ["agent-1", "agent-2", "agent-3"]
    
    fl_request = {
        "round_id": f"cli-round-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "model_base": "model-v1.0",
        "participants": participants,
        "epsilon_budget": 1.0,
        "timeout_minutes": 30,
        "validation_config": {
            "fairness_threshold": 0.8,
            "max_delta_size": 1048576
        }
    }
    
    response = requests.post(
        f"{SERVICES['fl-orchestrator']}/v1/fl/round",
        json=fl_request
    )
    
    print(f"FL round start: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def resolve_conflict():
    """Submit a conflict for arbitration"""
    conflict_request = {
        "conflict_set": {
            "conflict_id": f"cli-conflict-{uuid.uuid4()}",
            "agents": ["agent-1", "agent-2"],
            "positions": {
                "agent-1": {
                    "action": "scale_up",
                    "priority": 8,
                    "cost": 100
                },
                "agent-2": {
                    "action": "optimize",
                    "priority": 6, 
                    "cost": 50
                }
            },
            "context": {
                "resource_type": "compute",
                "urgency": "medium"
            }
        },
        "resolution_method": "auto",
        "priority": "normal"
    }
    
    response = requests.post(
        f"{SERVICES['arbiter']}/v1/arbiter/decide",
        json=conflict_request
    )
    
    print(f"Conflict resolution: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def publish_message(topic="test", message=None):
    """Publish message to consensus bus"""
    if message is None:
        message = {"type": "test", "data": "cli test message"}
    
    publish_request = {
        "topic": topic,
        "payload": message,
        "source": "cli-tool",
        "metadata": {"priority": "normal"}
    }
    
    response = requests.post(
        f"{SERVICES['consensus-bus']}/v1/publish",
        json=publish_request
    )
    
    print(f"Message publish: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def health_check():
    """Check health of all services"""
    print("=== CIN Service Health Check ===")
    for service, url in SERVICES.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            status = "✅ HEALTHY" if response.status_code == 200 else f"❌ UNHEALTHY ({response.status_code})"
            print(f"{service:20} {status}")
        except Exception as e:
            print(f"{service:20} ❌ ERROR: {e}")

def precheck():
    """Run basic precheck validation"""
    print("=== CIN Precheck ===")
    
    # Check service availability
    all_healthy = True
    for service, url in SERVICES.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code != 200:
                all_healthy = False
                print(f"❌ {service} not healthy")
            else:
                print(f"✅ {service} healthy")
        except:
            all_healthy = False
            print(f"❌ {service} not reachable")
    
    # Test basic workflow
    if all_healthy:
        print("\n--- Testing basic workflow ---")
        try:
            # Test signal ingestion
            ingest_signal("event", {"test": "precheck"})
            print("✅ Signal ingestion working")
            
            # Test message publishing
            publish_message("precheck", {"test": "precheck"})
            print("✅ Message publishing working")
            
            print("\n🎉 Basic precheck PASSED")
        except Exception as e:
            print(f"❌ Workflow test failed: {e}")
    else:
        print("\n⚠️  Precheck FAILED - services not healthy")

def main():
    if len(sys.argv) < 2:
        print("Usage: python sample_cli.py <command>")
        print("Commands:")
        print("  health       - Check service health")
        print("  precheck     - Run basic validation")
        print("  ingest       - Ingest test signal")
        print("  fl-round     - Start FL round")
        print("  conflict     - Resolve test conflict")
        print("  publish      - Publish test message")
        return
    
    command = sys.argv[1]
    
    if command == "health":
        health_check()
    elif command == "precheck":
        precheck()
    elif command == "ingest":
        ingest_signal()
    elif command == "fl-round":
        start_fl_round()
    elif command == "conflict":
        resolve_conflict()
    elif command == "publish":
        publish_message()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()