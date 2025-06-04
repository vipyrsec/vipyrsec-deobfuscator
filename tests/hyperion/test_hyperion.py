import re

from vipyr_deobf.deobfuscators.Hyperion.hyperion import hyperion_deobf


def test_deobf_hello_world():
    with open('tests/hyperion/sample_array.obf', 'r') as file:
        obf = file.read()
    code = hyperion_deobf.deobf(obf)
    assert re.search(r'np\.zeros\(10\s?\*\*\s?14\)', code)
    assert re.search(r'print\(\w+\)', code)
