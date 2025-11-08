def test_openapi_present():
    import os
    assert os.path.exists('infra/contracts/l7/openapi_l7.yaml')
