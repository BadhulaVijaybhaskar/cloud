import os, pytest
SIM = os.getenv('SIMULATION_MODE','true') == 'true'

def test_smoke():
    # Basic verification: in simulation mode we simply pass
    if SIM:
        assert True
    else:
        # Placeholder for live tests
        assert False, "Live tests not configured in this stub"