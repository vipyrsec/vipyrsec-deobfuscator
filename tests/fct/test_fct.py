import ast

from vipyr_deobf.deobfuscators.FCT.fct import fct_deobf


def test_deobf_hello_world():
    with open('tests/fct/sample_hello_world.obf', 'r') as file:
        obf = file.read()
    res = fct_deobf.deobf(obf).decode()
    with open('tests/fct/sample_hello_world.exp', 'r') as file:
        exp = file.read()
    assert ast.dump(ast.parse(res)) == ast.dump(ast.parse(exp))
