from src.vyze import read_layer_token, AccessGroup, read_access_group, read_layer_profile


def test_read_layer_token__1():
    token = read_layer_token('971f8594101187a92e866d2a3c8211ec21658b2d047d281cc515c7ff90670b5501ffffff00000000000000000000000062b786c17ffffffff3caa6adc7a83eea1780e9b68f9dac8ef22f0ce7')
    assert token.user_id == '971f8594101187a92e866d2a3c8211ec'
    assert token.layer_id == '21658b2d047d281cc515c7ff90670b55'
    assert token.granted == 33554431
    # assert token._created.timestamp() == 1656063581
    # assert token._expiry.seconds == 86399
    assert token.expires.timestamp() == 3803678400
    assert token.signature.hex() == 'c7a83eea1780e9b68f9dac8ef22f0ce7'
    assert token.token == '971f8594101187a92e866d2a3c8211ec21658b2d047d281cc515c7ff90670b5501ffffff00000000000000000000000062b786c17ffffffff3caa6adc7a83eea1780e9b68f9dac8ef22f0ce7'


def test_access_group():
    ag = AccessGroup('ag1', 0)
    tk1 = read_layer_token('971f8594101187a92e866d2a3c8211ec0fc053e11df777aa9f0e9b2480e1402001ffffff00000000000000000000000062b786f37fffffff0c00f47fc5ea88f2d97341609b06bd2e1e19df6b')
    tk2 = read_layer_token('971f8594101187a92e866d2a3c8211ec21658b2d047d281cc515c7ff90670b5501ffffff00000000000000000000000062b786970001517f4252ecc044db98184e77cf1d6768906fc931f5cc')
    ag.register_layer_token(tk1)
    ag.register_layer_token(tk2)
    assert len(ag.layer_tokens) == 2
    ag.unregister_layer_token(tk2.token)
    assert len(ag.layer_tokens) == 1


def test_access_group_string():
    ags = 'test:1ffffff:971f8594101187a92e866d2a3c8211ec0fc053e11df777aa9f0e9b2480e1402001ffffff00000000000000000000000062b786f37fffffff0c00f47fc5ea88f2d97341609b06bd2e1e19df6b,' \
          '971f8594101187a92e866d2a3c8211ec21658b2d047d281cc515c7ff90670b5501ffffff00000000000000000000000062b786970001517f4252ecc044db98184e77cf1d6768906fc931f5cc'
    ag = read_access_group(ags)
    assert str(ag) == ags


def test_layer_profile_string():
    lps = 'a:1ffffff:971f8594101187a92e866d2a3c8211ec21658b2d047d281cc515c7ff90670b5501ffffff00000000000000000000000062b786d87fffffffe6679ef20c46f438ce07b2f84e2d032f6922d210;' \
          'b:4924ea:971f8594101187a92e866d2a3c8211ec0fc053e11df777aa9f0e9b2480e14020004924ea00000000000000000000000062b786ea7fffffffabff5481b09e8c08a3d8aeb663194db2bf9baed9'
    lp = read_layer_profile(lps)
    assert lp._access_groups['a']
    assert lp._access_groups['b']
