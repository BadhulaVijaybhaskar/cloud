#!/usr/bin/env python3
import os
import subprocess
import sys

# Set simulation mode
os.environ['SIMULATION_MODE'] = 'true'

# Run the contract tests
result = subprocess.run([
    sys.executable, '-m', 'pytest', 
    'tests/k6/contract_tests.py', 
    '-v'
], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("STDERR:")
print(result.stderr)
print(f"Return code: {result.returncode}")

# Save test output
with open('reports/k6/pytest_output.txt', 'w') as f:
    f.write(f"Return code: {result.returncode}\n")
    f.write("STDOUT:\n")
    f.write(result.stdout)
    f.write("\nSTDERR:\n")
    f.write(result.stderr)