from src.vyze import ServiceClient
from src.vyze.tests.test_client import service_url


def test_service__resolve_universe():
    sc = ServiceClient(service_url)
    data_id = sc.resolve_universe('data')
    assert len(data_id) > 0


def test_service__load_universe__public():
    sc = ServiceClient(service_url)
    data_univ = sc.load_universe(sc.resolve_universe('data'))
    assert len(data_univ.models) > 0
    assert data_univ['base.object']


# def test_service__load_universe__private():
#     sc = ServiceClient('http://localhost:9150')
#     sc.set_token('lx-FlBARh6kuhm0qPIIR7BBUJsXxCeIlHmQMVIAjdt0AAAAAAAAAAAAAAAAAAAAAY3q3YgAAAACAUQEA/BJ7Riz7aN_K5Wggo3dkz3InLhFo')
#     data_univ = sc.load_universe(sc.resolve_universe('private_universe'))
#     assert len(data_univ.models) > 0
#     assert data_univ['base.object']


# def test_service__layer_profile():
#     sc = ServiceClient(service_url)
#     sc.set_token('lx-FlBARh6kuhm0qPIIR7AAAAAAAAAAAAAAAAAAAAABsbvhtBDmszI_Ya8fqTM96Fde4YgAAAAD___9_/hfo2aZSR2Cl09Gxcm3zdDXEfr2I')
#     # univ = sc.load_universe('18ce41cfb98e0c26d5f12797782dac68')
#     profile = sc.get_layer_profile('6c6ef86d0439accc8fd86bc7ea4ccf7a')
#     print(profile)
