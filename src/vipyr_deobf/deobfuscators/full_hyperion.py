"""
Full deobfuscator for hyperion

Status: INCOMPLETE
"""

import ast
import binascii
import zlib
from ast import *
from io import BytesIO
from typing import Any, TextIO


class FirstLayer(NodeVisitor):
    def __init__(self):
        self.second_layer_bytes = BytesIO()
        self.func_info = {}

    def visit_Call(self, node: Call):
        match node:
            case Call(
                func=Attribute(),
                args=[],
                keywords=[
                    keyword(value=Constant(value=str())),
                    keyword(value=Constant(value=bytes(payload))),
                ]
            ):
                self.second_layer_bytes.write(payload)
            case _:
                pass


def simplify(node: AST, var_dict: dict[str, Any]) -> Any:
    match node:
        case Constant(value=str(value) | bytes(value)):
            return value
        case Subscript(Constant(value=str(value))):
            return value[::-1]
        case Call(
            func=Attribute(
                value=Call(
                    func=Name(id=unhexlify_func),
                    args=[Constant(value=bytes(value))],
                ),
                attr='decode',
            ),
            args=[Subscript(value=Constant(value='8ftu'))]
        ) if var_dict.get(unhexlify_func, None) is binascii.unhexlify:
            return binascii.unhexlify(value).decode('utf8')
        case _:
            raise ValueError('\n\n' + ast.dump(node, indent=2))


def full_hyperion_deobf(file: TextIO) -> str:
    ast_tree = ast.parse(file.read())
    first_layer = FirstLayer()
    first_layer.visit(ast_tree)
    second_layer_bytes = first_layer.second_layer_bytes
    second_layer = zlib.decompress(second_layer_bytes.getvalue()).decode()

    second_layer_tree = ast.parse(second_layer)
    body = second_layer_tree.body
    assert isinstance(body[0], Try)
    body[:1] = []

    var_dict = {}
    while True:
        node = body[0]
        match node:
            case Assign(
                targets=[Subscript(
                    value=Call(),
                    slice=name_expr)],
                value=value_expr,
            ):
                var_dict[simplify(name_expr, var_dict)] = simplify(value_expr, var_dict)
                body[:1] = []
            case _:
                break


if __name__ == '__main__':
    with open('/Users/stickie/PycharmProjects/mantis-deobfuscator/test_file.txt', 'r') as file:
        full_hyperion_deobf(file)
