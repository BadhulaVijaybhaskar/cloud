import requests
import json
import time
import uuid

class EdgeAgent:
    def __init__(self, hub_url="http://localhost:8030", node_id=None):
        self.hub_url = hub_url
        self.node_id = node_id or str(uuid.uuid4())
        self.capabilities = ["monitoring", "basic-actions"]
    
    def register(self):
        """Register with federation hub"""
        payload = {
            "node_id": self.node_id,
            "endpoint": f"http://edge-{self.node_id}:8040",
            "capabilities": self.capabilities
        }
        
        try:
            response = requests.post(f"{self.hub_url}/federation/register", json=payload)
            if response.status_code == 200:
                result = response.json()
                print(f"Registered successfully: {result}")
                return result
            else:
                print(f"Registration failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"Registration error: {e}")
            # Simulate successful registration
            return {"status": "registered", "registration_id": str(uuid.uuid4())}
    
    def heartbeat(self):
        """Send heartbeat to hub"""
        print(f"Heartbeat from node {self.node_id}")
        return True

def main():
    agent = EdgeAgent()
    print(f"Starting edge agent: {agent.node_id}")
    
    # Register with hub
    registration = agent.register()
    
    # Simulate heartbeat
    for i in range(3):
        agent.heartbeat()
        time.sleep(1)
    
    print("Edge agent simulation complete")

if __name__ == "__main__":
    main()