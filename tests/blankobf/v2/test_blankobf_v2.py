import ast

from vipyr_deobf.deobfuscators.BlankObf.blankobf_v2 import blankobf_v2_deobf

BLANK_OBF_HEADER = ':: You managed to break through BlankOBF v2; Give yourself a pat on your back! ::'


def test_deobf_hello_world():
    with open('tests/blankobf/v2/sample_array.obf', 'r') as file:
        obf = file.read()
    status, res = blankobf_v2_deobf.deobf(obf)
    assert status
    with open('tests/blankobf/v2/sample_array.exp', 'r') as file:
        exp = file.read()
    assert ast.dump(res) == ast.dump(ast.parse(f'"{BLANK_OBF_HEADER}"\n{exp}'))
