from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI(title="ATOM Quantum Runtime Adapter", version="1.0.0")

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
QUANTUM_PROVIDER = os.getenv("QUANTUM_PROVIDER", "mock")

class QuantumCircuit(BaseModel):
    circuit_data: str
    shots: int = 1024
    backend: str = "qasm_simulator"

@app.get("/health")
def health():
    return {"status": "healthy", "service": "quantum-runtime-adapter", "simulation": SIMULATION_MODE}

@app.post("/quantum/execute")
def execute_quantum_circuit(circuit: QuantumCircuit):
    """Execute quantum circuit"""
    if SIMULATION_MODE:
        # Simulate quantum execution
        return {
            "job_id": f"qjob_{circuit.backend}_{datetime.now().strftime('%H%M%S')}",
            "status": "completed",
            "shots": circuit.shots,
            "backend": circuit.backend,
            "results": {
                "counts": {"00": 512, "11": 512},
                "execution_time_ms": 250
            },
            "quantum_volume": 64,
            "simulation": True
        }
    
    # Real Qiskit integration would go here
    try:
        # Placeholder for qiskit import
        return {"error": "Qiskit runtime unavailable"}
    except ImportError:
        return {"error": "Quantum libraries not installed"}

@app.get("/quantum/backends")
def list_quantum_backends():
    """List available quantum backends"""
    if SIMULATION_MODE:
        return {
            "backends": [
                {"name": "qasm_simulator", "type": "simulator", "qubits": 32},
                {"name": "statevector_simulator", "type": "simulator", "qubits": 20},
                {"name": "mock_qpu", "type": "hardware", "qubits": 5}
            ]
        }
    
    return {"error": "Backend listing unavailable"}

@app.get("/quantum/status")
def quantum_status():
    """Get quantum runtime status"""
    if SIMULATION_MODE:
        return {
            "provider": QUANTUM_PROVIDER,
            "available_backends": 3,
            "queue_length": 2,
            "avg_execution_time_ms": 300
        }
    
    return {"error": "Quantum status unavailable"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8701)