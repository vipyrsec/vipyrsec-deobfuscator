import ast

from vipyr_deobf.deobfuscators.Vare.vare import vare_deobf


def test_deobf_hello_world():
    with open('tests/vare/v1/sample_hello_world.obf', 'r') as file:
        obf = file.read()
    code = vare_deobf.deobf(obf)
    with open('tests/vare/v1/sample_hello_world.exp', 'r') as file:
        exp = file.read()
    assert ast.dump(ast.parse(code)) == ast.dump(ast.parse(exp))
