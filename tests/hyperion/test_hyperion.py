import pytest

from vipyr_deobf.deobfuscators.Hyperion.hyperion import hyperion_deobf


@pytest.mark.skip("Hyperion deobf doesn't preserve names")
def test_deobf_hello_world():
    with open('tests/hyperion/sample_array.obf', 'r') as file:
        obf = file.read()
    code = hyperion_deobf.deobf(obf)
    with open('tests/hyperion/sample_array.exp', 'r') as file:
        exp = file.read()
    assert False
