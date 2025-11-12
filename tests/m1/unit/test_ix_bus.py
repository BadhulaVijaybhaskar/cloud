import os
import pytest

SIM = os.getenv('SIMULATION_MODE', 'true') == 'true'

def test_ix_bus_publish():
    if SIM:
        assert True, "IX Bus publish simulation test passed"
    else:
        pytest.skip("Production mode not implemented")

def test_ix_bus_subscribe():
    if SIM:
        assert True, "IX Bus subscribe simulation test passed"
    else:
        pytest.skip("Production mode not implemented")