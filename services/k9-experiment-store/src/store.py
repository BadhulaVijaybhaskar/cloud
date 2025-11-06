#!/usr/bin/env python3
import os, json
STORE = os.getenv("EXPERIMENT_STORE","data/k9_experiments.json")
os.makedirs(os.path.dirname(STORE), exist_ok=True)
def save(experiment):
    data = []
    if os.path.exists(STORE):
        try:
            data=json.load(open(STORE))
        except:
            data=[]
    data.append(experiment)
    json.dump(data, open(STORE,"w"), indent=2)
    return True

if __name__=="__main__":
    save({"id":"exp-001","notes":"initial stub"})
    print("Saved experiment")