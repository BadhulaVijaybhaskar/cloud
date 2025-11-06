# services/partner-onboard-worker/src/worker.py
import os, json, time

SIM = os.getenv("SIMULATION_MODE", "true") == "true"
REPORTS="reports/k7"

def seed_partners(count=3):
    os.makedirs(REPORTS, exist_ok=True)
    for i in range(1, count+1):
        pid = f"partner-test-{i}"
        obj = {"partner_id":pid,"name":f"Partner {i}","email":f"partner{i}@example.com","status":"seeded"}
        with open(f"{REPORTS}/{pid}.json","w") as f:
            json.dump(obj,f)
    print(f"Seeded {count} partners")

if __name__=="__main__":
    c = int(os.getenv("PARTNER_BETA_COUNT","3"))
    seed_partners(c)