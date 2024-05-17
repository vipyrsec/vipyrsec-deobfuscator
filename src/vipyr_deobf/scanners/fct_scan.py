import ast
from ast import (Assign, Attribute, Call, Constant, Expr, Lambda, Name, Slice,
                 Subscript, UnaryOp, USub, arg, arguments)


def match_inner_underscore_function(node: ast.Call):
    match node:
        case Call(
            func=Attribute(
                value=Call(
                    func=Name(id='__import__'),
                    args=[Constant(value='zlib')]
                ),
                attr='decompress',
            ),
            args=[
                Call(
                    func=Attribute(
                        value=Call(
                            func=Name(id='__import__'),
                            args=[Constant(value='base64')]
                        ),
                        attr='b64decode',
                    ),
                    args=[
                        Subscript(
                            value=Name(id='__'),
                            slice=Slice(
                                step=UnaryOp(op=USub(), operand=Constant(value=1))),
                        )
                    ]
                )
            ]
        ):
            return True
    return False


class FCTScanner(ast.NodeVisitor):
    def __init__(self):
        self.underscore_function_found = False
        self.payload_found = False

    def visit_Assign(self, node):
        match node:
            case Assign(
                targets=[Name(id='_')],
                value=Lambda(
                    args=arguments(args=[arg(arg='__')]),
                    body=Call(
                        func=Attribute(
                            value=Call(
                                func=Name(id='__import__'),
                                args=[Constant(value='marshal')]
                            ),
                            attr='loads',
                        ),
                        args=[body]
                    ) | body
                )
            ) if match_inner_underscore_function(body):
                self.underscore_function_found = True
                return

    def visit_Expr(self, node):
        match node:
            case Expr(
                value=Call(
                    func=Name(id='exec'),
                    args=[
                        Call(
                            func=Name(id='_'),
                            args=[Constant(value=payload)]
                        )
                    ]
                )
            ) if isinstance(payload, bytes):
                self.payload_found = True
                return


def scan_fct(code: str):
    fct_scanner = FCTScanner()
    fct_scanner.visit(ast.parse(code))
    return (
        fct_scanner.underscore_function_found
        and fct_scanner.payload_found
    )
