#!/usr/bin/env python3
import json,sys,os
infile = sys.argv[1] if len(sys.argv)>1 else '/workspace/atom-cloud/reports/i9/I9_pytest_report.json'
outfile = sys.argv[2] if len(sys.argv)>2 else '/workspace/atom-cloud/reports/i9/I9_governance_test_report.json'
data = {}
if os.path.exists(infile):
    with open(infile,'r') as f:
        data['pytest'] = json.load(f)
else:
    data['pytest'] = {"note":"simulated","passed":0,"failed":0}
# minimal evidence: collect last git commit
import subprocess
try:
    commit = subprocess.check_output(['git','rev-parse','--short','HEAD']).decode().strip()
except Exception:
    commit = 'local'
data['git_commit'] = commit
with open(outfile,'w') as f:
    json.dump(data,f,indent=2)
print("Wrote", outfile)