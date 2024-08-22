import ast

from vipyr_deobf.deobfuscators import fct


def test_deobf_hello_world():
    with open('tests/fct/sample_hello_world.obf', 'r') as file:
        obf = file.read()
    res = fct.deobf_fct(obf).decode()
    with open('tests/fct/sample_hello_world.exp', 'r') as file:
        exp = file.read()
    assert ast.dump(ast.parse(res)) == ast.dump(ast.parse(exp))
