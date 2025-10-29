# Compliance Precheck — Phase H.3 Quantum-AI Readiness

Purpose: verify quantum runtime and PQC bridge before execution.  
Output: `/reports/H.3_precheck.json`.

Checks:
1. Vault & Cosign presence  
2. Neural fabric bridge endpoint `/pqc/handshake` → 200 OK  
3. Quantum runtime availability (Qiskit import check)  
4. Env defaults exist (`.env.default`)  

Decision Rules:  
- All OK → PROCEED  
- Quantum runtime missing → PROCEED_SIMULATION  
- Vault missing → BLOCK